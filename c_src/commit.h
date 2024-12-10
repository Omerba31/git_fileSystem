#ifndef COMMIT_H
#define COMMIT_H

#include <string>
#include <ctime> // For std::time_t

class Commit {
public:
    const std::string treeHash;  // Hash of the tree object
    const std::string author;    // Author of the commit
    const std::string message;   // Commit message
    const std::time_t timestamp; // Timestamp of the commit

    Commit(const std::string& treeHash, const std::string& author, const std::string& message, std::time_t timestamp):
            treeHash(treeHash), author(author), message(message), timestamp(timestamp) {}

};

#endif // COMMIT_H
