#include "hashTypes.h"
#include "caf.h"

// Compute hash for Blob
std::string hash_object(const Blob& blob) {
    return blob.hash;
}

// Compute hash for Tree
std::string hash_object(const Tree& tree) {
    std::string acc_std;
    for (const auto& [key, record] : tree.records) {
        acc_std += record.name + std::to_string(static_cast<int>(record.type)) + record.hash;
    }
    return hash_string(acc_std);
}

// Compute hash for Commit
std::string hash_object(const Commit& commit) {
    std::string acc_std;
    acc_std += commit.treeHash + commit.author + commit.message + std::to_string(commit.timestamp) + commit.parent.value_or("");
    return hash_string(acc_std);
}