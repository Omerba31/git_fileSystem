#ifndef OPEN_FILE_H
#define OPEN_FILE_H

#define HASH_SIZE 40     // SHA-1 hash size (in characters)
#define BUFFER_SIZE 4096 // Buffer size for file operations

#include "save_hash.h"
#include "delete_hash.h"
#include "sha1_utils.h"

// Function declarations
void compute_sha1(const char *file_path, char *hash);
void save_file_based_on_hash(const char *file_path, const char *hash);
int open_file_by_hash(const char *filename);
int open_file(const char *file_path);

#endif // OPEN_FILE_H