#include "commit.h"

// Constructor
Commit::Commit(const std::string& treeHash, const std::string& author, const std::string& message, std::time_t timestamp)
    : treeHash(treeHash), author(author), message(message), timestamp(timestamp) {}

// Getters
const std::string& Commit::getTreeHash() const {
    return treeHash;
}

const std::string& Commit::getAuthor() const {
    return author;
}

const std::string& Commit::getMessage() const {
    return message;
}

std::time_t Commit::getTimestamp() const {
    return timestamp;
}


