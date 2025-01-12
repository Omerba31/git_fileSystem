#include "object_io.h"
#include "hashTypes.h"
#include "caf.h"
#include <map>
#include <string>
#include <unistd.h>    
#include <fcntl.h>     
#include <sys/file.h>  
#include <vector>      
#include <cstring>     
#include <stdexcept>   

// Helper function to read a length-prefixed string safely
bool read_length_prefixed_string(int fd, std::string &output) {
    uint32_t length;
    if (read(fd, &length, sizeof(length)) != sizeof(length)) {
        return false;  
    }

    if (length > MAX_LENGTH) {
        return false;  
    }

    // Read the actual string
    std::vector<char> buffer(length + 1);
    if (read(fd, buffer.data(), length) != static_cast<ssize_t>(length)) {
        return false;  
    }
    buffer[length] = '\0';  
    output.assign(buffer.data());
    return true;
}

// Helper function to clean up resources
int cleanup(int fd, const std::string &root_dir, const std::string &hash, bool deleteContent) {
    if (fd >= 0) {
        flock(fd, LOCK_UN);
        close(fd);
    }
    if (deleteContent) {
        delete_content(root_dir.c_str(), hash.c_str());
        return -1;
    }
    return 0;
}

bool write_with_length(int fd, const std::string &data) {
    uint32_t length = data.length();
    if (write(fd, &length, sizeof(length)) != sizeof(length) ||
        write(fd, data.c_str(), length) != static_cast<ssize_t>(length)) {
        return false;
    }
    return true;
}

// Serialize Commit to disk
int save_commit(const std::string &root_dir, const Commit &commit) {
    std::string commit_hash = hash_object(commit);

    int fd = open_content_for_saving_fd(root_dir, commit_hash);
    if (fd < 0) {
        return -1;
    }
    
    if (!write_with_length(fd, commit.treeHash)) {
        return cleanup(fd, root_dir, commit_hash, true);
    }
    if (!write_with_length(fd, commit.author)) {
        return cleanup(fd, root_dir, commit_hash, true);
    }
    if (!write_with_length(fd, commit.message)) {
        return cleanup(fd, root_dir, commit_hash, true);
    }
    if (write(fd, &commit.timestamp, sizeof(commit.timestamp)) != sizeof(commit.timestamp)) {
        return cleanup(fd, root_dir, commit_hash, true);
    }
    if (commit.parent) {
        if (!write_with_length(fd, *commit.parent)) {
            return cleanup(fd, root_dir, commit_hash, true);
        }
    } else {
        // If parent doesnt exists write 0 length string
        uint32_t length = 0;
        if (write(fd, &length, sizeof(length)) != sizeof(length)) {
            return cleanup(fd, root_dir, commit_hash, true);
        }
    }
    // Cleanup without deleting content
    return cleanup(fd, root_dir, commit_hash, false);
}

// Deserialize Commit from disk
std::pair<int, Commit> load_commit(const std::string &root_dir, const std::string &hash) {
    int fd = open_content_for_reading_fd(root_dir.c_str(), hash.c_str());
    if (fd < 0) {
        return {-1, Commit()}; 
    }

    std::string treehash;
    if (!read_length_prefixed_string(fd, treehash)) {
        cleanup(fd, root_dir, hash, true);
        return {-1, Commit()};
    }
    std::string author;
    if (!read_length_prefixed_string(fd, author)) {
        cleanup(fd, root_dir, hash, true);
        return {-1, Commit()};  // Failed to read author
    }
    std::string message;
    if (!read_length_prefixed_string(fd, message)) {
        cleanup(fd, root_dir, hash, true);
        return {-1, Commit()};
    }
    uint64_t timestamp;
    if (read(fd, &timestamp, sizeof(timestamp)) != sizeof(timestamp)) {
        cleanup(fd, root_dir, hash, true);
        return {-1, Commit()};
    }

    std::string parent;
    if (!read_length_prefixed_string(fd, parent)) {
        cleanup(fd, root_dir, hash, true);
        return {-1, Commit()};
    }

    cleanup(fd, root_dir, hash, false);
    Commit commit(treehash, author, message, timestamp, parent.empty() ? std::nullopt : std::make_optional(parent));
    return {0, commit};
}

// Helper function to serialize a TreeRecord
bool write_tree_record(int fd, const TreeRecord &record) {
    uint8_t type = static_cast<uint8_t>(record.type);
    if (write(fd, &type, sizeof(type)) != sizeof(type)) {
        return false;
    }
    if (!write_with_length(fd, record.hash) || !write_with_length(fd, record.name)) {
        return false;
    }
    return true;
}

// Helper function to deserialize a TreeRecord
std::pair<int, TreeRecord> read_tree_record(int fd) {
    uint8_t type;
    if (read(fd, &type, sizeof(type)) != sizeof(type)) {
        return {-1, TreeRecord(TreeRecord::Type::TREE, "", "")}; // Return failure
    }
    TreeRecord::Type recordType = static_cast<TreeRecord::Type>(type);
    std::string hash, name;
    if (!read_length_prefixed_string(fd, hash) || !read_length_prefixed_string(fd, name)) {
        return {-1, TreeRecord(TreeRecord::Type::TREE, "", "")}; // Return failure
    }
    TreeRecord record(recordType, hash, name);
    return {0, record};
}


// Serialize Tree to disk
int save_tree(const std::string &root_dir, const Tree &tree) {
    std::string tree_hash = hash_object(tree);

    int fd = open_content_for_saving_fd(root_dir, tree_hash);
    if (fd < 0) {
        return -1;
    }

    uint32_t num_records = tree.records.size();
    if (write(fd, &num_records, sizeof(num_records)) != sizeof(num_records)) {
        return cleanup(fd, root_dir, tree_hash, true);
    }
    for (const auto &[name, record] : tree.records) {
        if (!write_tree_record(fd, record)) {
            return cleanup(fd, root_dir, tree_hash, true);
        }
    }
    return cleanup(fd, root_dir, tree_hash, false);
}

// Deserialize Tree from disk
std::pair<int, Tree> load_tree(const std::string &root_dir, const std::string &hash) {
    int fd = open_content_for_reading_fd(root_dir.c_str(), hash.c_str());
    if (fd < 0) {
        return {-1, Tree({})};
    }

    uint32_t num_records;
    if (read(fd, &num_records, sizeof(num_records)) != sizeof(num_records)) {
        cleanup(fd, root_dir, hash, true);
        return {-1, Tree({})};
    }
    std::map<std::string, TreeRecord> records;
    for (uint32_t i = 0; i < num_records; ++i) {
        auto [status, record] = read_tree_record(fd);
        if (status != 0) {
            cleanup(fd, root_dir, hash, true);
            return {-1, Tree({})};
        }
        records.emplace(record.name, std::move(record));
    }
    cleanup(fd, root_dir, hash, false);
    return {0, Tree(records)};
}
