#ifndef COMMIT_H
#define COMMIT_H

#include <string>
#include <ctime> // For std::time_t
#include <optional> // For std::optional

class Commit {
public:
    const std::string treeHash;  // Hash of the tree object
    const std::string author;    // Author of the commit
    const std::string message;   // Commit message
    const std::time_t timestamp; // Timestamp of the commit
    const std::optional<std::string> parent; // Parent commit hash

    // Default constructor
    Commit(): treeHash(""), author(""), message(""), timestamp(0), parent(std::nullopt) {}

    Commit(const std::string& treeHash, const std::string& author, const std::string& message, std::time_t timestamp, std::optional<std::string> parent = std::nullopt):
            treeHash(treeHash), author(author), message(message), timestamp(timestamp), parent(parent) {}

};

#endif // COMMIT_H
