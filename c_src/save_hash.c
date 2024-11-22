#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <linux/limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <linux/limits.h>
#include "save_hash.h"
#include "utils.h"
#include "sha1_utils.h"

#define HASH_SIZE 40     // SHA-1 hash size (in characters)
#define BUFFER_SIZE 4096 // Buffer size for file operations

void save_file(const char *root_dir, const char *filename) {
    // Compute the SHA1 hash of the file
    char hash[HASH_SIZE + 1];
    compute_sha1(filename, hash);

    // Create the root directory if it does not exist
    mkdir(root_dir, 0755);
    // Create the directory structure based on the first two characters of the hash
    char dir_name[PATH_MAX];
    strcpy(dir_name, root_dir);
    strcat(dir_name, "/");
    strncat(dir_name, hash, 2);
    mkdir(dir_name, 0755);

    // Construct the file path using the hash
    char file_path[PATH_MAX];

    strcpy(file_path, dir_name);
    strcat(file_path, "/");
    strcat(file_path, hash);

    // Check if the file already exists
    struct stat file_stat;
    if (stat(file_path, &file_stat) == 0) {
        return;
    }
    // Copy the file to the new location
    if (copy_file(filename, file_path) != 0) {
        exit(EXIT_FAILURE);
        exit(EXIT_FAILURE);
    }
}
