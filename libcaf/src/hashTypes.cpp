#include "hashTypes.h"
#include "caf.h"
#include <sstream>
#include <stdexcept>

// Compute hash for Blob
std::string computeHash(const Blob& blob) {
    return blob.hash;
}

// Compute hash for Tree
std::string computeHash(const Tree& tree) {
    std::ostringstream oss;
    for (const auto& [key, record] : tree.records) {
        //add the already calculated hash of each record
        oss << record.name.c_str() << std::to_string(static_cast<int>(record.type)) << record.hash.c_str();
    }

    std::string treeHash;
    if (compute_hash(oss.str(), treeHash) != 0)
        throw std::runtime_error("Failed to compute SHA1 hash for Tree");

    return treeHash;
}

// Compute hash for Commit
std::string computeHash(const Commit& commit) {
    std::ostringstream oss;
    oss << commit.treeHash << commit.author << commit.message << commit.timestamp <<commit.parent.value_or("");

    std::string commitHash;
    if (compute_hash(oss.str(), commitHash) != 0)
        throw std::runtime_error("Failed to compute SHA1 hash for Commit");

    return commitHash;
}