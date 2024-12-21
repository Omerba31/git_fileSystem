#ifndef CAF_H
#define CAF_H

#include <unistd.h>
#include <string>
#include <cstddef>

#define HASH_SIZE 40

int compute_hash(const char *filename, char *output);
int compute_hash(const std::string& input, std::string& output);
int open_content(const char *root_dir, const char *hash);
int save_content(const char *root_dir, const char *filename);
int delete_content(const char *root_dir, const char *hash);
int copy_file(const char *src, const char *dest);
int create_content_path(const char *root_dir, const char *hash, char *output_path, size_t output_size);
int create_sub_dir(const char *root_dir, const char *hash);
int lock_file_with_timeout(int fd, int operation, int timeout_sec);

#endif // CAF_H