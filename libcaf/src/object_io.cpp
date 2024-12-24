#include "object_io.h"
#include "hashTypes.h"
#include "caf.h"
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

// Save Commit to disk
int save_commit(const std::string &root_dir, const Commit &commit) {
    std::string commit_hash = computeHash(commit);

    auto [status, fd, blob_path] = save_content(root_dir, commit_hash, O_WRONLY | O_CREAT);
    if (status != 0) {
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

    // Cleanup without deleting content
    return cleanup(fd, root_dir, commit_hash, false);
}

// Load Commit from disk
std::pair<int, Commit> load_commit(const std::string &root_dir, const std::string &hash) {
    // Open the commit file using open_content
    int fd = open_content(root_dir.c_str(), hash.c_str());
    if (fd < 0) {
        return {-1, Commit()}; 
    }

    try {
        // Read and validate the treehash
        std::string treehash;
        if (!read_length_prefixed_string(fd, treehash)) {
            flock(fd, LOCK_UN);
            close(fd);
            return {-1, Commit()};
        }

        // Read and validate the author
        std::string author;
        if (!read_length_prefixed_string(fd, author)) {
            flock(fd, LOCK_UN);
            close(fd);
            return {-1, Commit()};  // Failed to read author
        }

        // Read and validate the message
        std::string message;
        if (!read_length_prefixed_string(fd, message)) {
            flock(fd, LOCK_UN);
            close(fd);
            return {-1, Commit()}; 
        }

        // Read the timestamp
        uint64_t timestamp;
        if (read(fd, &timestamp, sizeof(timestamp)) != sizeof(timestamp)) {
            flock(fd, LOCK_UN);
            close(fd);
            return {-1, Commit()};
        }

        // Unlock and close the file
        flock(fd, LOCK_UN);
        close(fd);

        Commit commit(treehash, author, message, timestamp);
        return {0, commit};
    } catch (...) {
        // Unlock and close the file in case of any error
        flock(fd, LOCK_UN);
        close(fd);
        return {-1, Commit()}; 
    }
}