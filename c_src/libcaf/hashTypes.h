#ifndef HASHTYPES_H
#define HASHTYPES_H

#include <string>
#include "Blob.h"
#include "treeRecord.h"
#include "Tree.h"
#include "commit.h"

// Function declarations for computing hashes
std::string computeHash(const Blob& blob);
std::string computeHash(const Tree& tree);
std::string computeHash(const Commit& commit);

#endif // HASHTYPES_H