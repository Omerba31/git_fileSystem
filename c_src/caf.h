#ifndef CAF_H
#define CAF_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <linux/limits.h>
#include <sys/file.h>
#include <openssl/evp.h>
#include <time.h>

#define HASH_SIZE 40
#define BUFFER_SIZE 4096
#define DIR_NAME_SIZE 2

#define PATH_ADVANCE(index)      \
    do                           \
    {                            \
        if ((index) >= PATH_MAX) \
        {                        \
            return -1;           \
        }                        \
        (index)++;               \
    } while (0)

// Function declarations
int compute_sha1(const char *filename, char *output);
int open_content(const char *root_dir, const char *hash);
int save_content(const char *root_dir, const char *filename);
int delete_content(const char *root_dir, const char *hash);
int copy_file(const char *src, const char *dest);
int create_content_path(const char *root_dir, const char *hash, char *output_path, size_t output_size);
int create_sub_dir(const char *root_dir, const char *hash);
int lock_file_with_timeout(int fd, int operation, int timeout_sec);

#endif // CAF_H