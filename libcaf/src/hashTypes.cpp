#include "hashTypes.h"
#include "caf.h"
#include <sstream>
#include <stdexcept>

// Compute hash for Blob
std::string hash_object(const Blob& blob) {
    return blob.hash;
}

// Compute hash for Tree
std::string hash_object(const Tree& tree) {
    std::ostringstream oss;
    for (const auto& [key, record] : tree.records) {
        oss << record.name.c_str() << std::to_string(static_cast<int>(record.type)) << record.hash.c_str();
    }
    return hash_string(oss.str());
}

// Compute hash for Commit
std::string hash_object(const Commit& commit) {
    std::ostringstream oss;
    oss << commit.treeHash << commit.author << commit.message << commit.timestamp <<commit.parent.value_or("");
    return hash_string(oss.str());
}