#include "Blob.h"
#include "treeRecord.h"
#include "Tree.h"
#include "commit.h"
#include "caf.h" // For compute_sha1
#include <string>
#include <sstream>
#include <stdexcept>

// Compute hash for Blob
std::string computeHash(const Blob& blob) {
    return blob.hash;
}

// Compute hash for TreeRecord
std::string computeHash(const TreeRecord& record) {
    std::ostringstream oss;
    oss << static_cast<int>(record.type) << record.hash << record.name;

    std::string combinedHash;
    if (compute_sha1(oss.str(), combinedHash) != 0)
        throw std::runtime_error("Failed to compute SHA1 hash for TreeRecord");

    return combinedHash;
}


// Compute hash for Tree
std::string computeHash(const Tree& tree) {
    std::ostringstream oss;
    for (const auto& [key, record] : tree.records) {
        oss << computeHash(record);
    }

    std::string treeHash;
    if (compute_sha1(oss.str(), treeHash) != 0)
        throw std::runtime_error("Failed to compute SHA1 hash for Tree");

    return treeHash;
}


// Compute hash for Commit
std::string computeHash(const Commit& commit) {
    std::ostringstream oss;
    oss << commit.treeHash << commit.author << commit.message << commit.timestamp;

    std::string commitHash;
    if (compute_sha1(oss.str(), commitHash) != 0)
        throw std::runtime_error("Failed to compute SHA1 hash for Commit");

    return commitHash;
}
