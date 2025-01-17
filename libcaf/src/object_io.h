#ifndef OBJECT_IO_H
#define OBJECT_IO_H

#include <string>
#include <utility>
#include <vector>
#include <stdexcept>
#include <cstdint>
#include "commit.h"
#include "Tree.h"

// Maximum string length for length-prefixed strings
constexpr uint32_t MAX_LENGTH = 1024 * 1024;  // 1 MB limit for strings

void save_commit(const std::string &root_dir, const Commit &commit);
Commit load_commit(const std::string &root_dir, const std::string &hash);
void save_tree(const std::string &root_dir, const Tree &tree);
Tree load_tree(const std::string &root_dir, const std::string &hash);


#endif // OBJECT_IO_H
