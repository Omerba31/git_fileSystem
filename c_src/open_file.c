#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <linux/limits.h>
#include <openssl/evp.h>
#include "file_utils.h"

#define HASH_SIZE 40     // SHA-1 hash size (in characters)
#define BUFFER_SIZE 4096 // Buffer size for file operations
#define DIR_NAME_SIZE 2  // Number of characters from hash used for directory name

// Function to open the file based on its hash
int open_content(const char *root_dir, const char *hash) {
    // Construct the file path using the first two characters of the hash and the root directory
    char file_path[PATH_MAX];
    int i = 0;

    // Copy the root directory path
    while (root_dir[i] != '\0') {
        file_path[i] = root_dir[i];
        i++;
    }

    // Ensure the root directory path ends with a '/'
    if (file_path[i - 1] != '/') {
        file_path[i++] = '/';
    }

    // Copy the first DIR_NAME_SIZE characters of the hash
    for (int j = 0; j < DIR_NAME_SIZE; j++) {
        file_path[i++] = hash[j];
    }
    file_path[i++] = '/';

    // Copy the full hash
    int j = 0;
    while (hash[j] != '\0') {
        file_path[i++] = hash[j++];
    }

    // Null-terminate the file path
    file_path[i] = '\0';

    // Open the file and return the file descriptor
    int fd = open(file_path, O_RDONLY);

    return fd;
}
