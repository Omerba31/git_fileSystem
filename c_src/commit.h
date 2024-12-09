#ifndef COMMIT_H
#define COMMIT_H

#include <string>
#include <ctime> // For std::time_t

class Commit {
private:
    const std::string treeHash;  // Hash of the tree object
    const std::string author;    // Author of the commit
    const std::string message;   // Commit message
    const std::time_t timestamp; // Timestamp of the commit

public:
    // Constructor
    Commit(const std::string& treeHash, const std::string& author, const std::string& message, std::time_t timestamp);

    // Getters
    const std::string& getTreeHash() const;
    const std::string& getAuthor() const;
    const std::string& getMessage() const;
    std::time_t getTimestamp() const;
};

#endif // COMMIT_H
