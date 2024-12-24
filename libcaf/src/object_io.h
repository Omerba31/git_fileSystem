#ifndef OBJECT_IO_H
#define OBJECT_IO_H

#include <string>
#include <utility>
#include <vector>
#include <stdexcept>
#include <cstdint>
#include "commit.h"

// Maximum string length for length-prefixed strings
constexpr uint32_t MAX_LENGTH = 1024 * 1024;  // 1 MB limit for strings

int save_commit(const std::string &root_dir, const Commit &commit);
std::pair<int, Commit> load_commit(const std::string &root_dir, const std::string &hash);

#endif // OBJECT_IO_H
