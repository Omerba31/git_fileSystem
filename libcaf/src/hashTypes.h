#ifndef HASHTYPES_H
#define HASHTYPES_H

#include <string>
#include "Blob.h"
#include "treeRecord.h"
#include "Tree.h"
#include "commit.h"

// Function declarations for computing hashes
std::string hash_object(const Blob& blob);
std::string hash_object(const Tree& tree);
std::string hash_object(const Commit& commit);

#endif // HASHTYPES_H