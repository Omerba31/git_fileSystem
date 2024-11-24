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
#include "file_utils.h"

#define HASH_SIZE 40     // SHA-1 hash size (in characters)
#define BUFFER_SIZE 4096 // Buffer size for file operations

int save_file(const char *root_dir, const char *filename) {
    // Compute the SHA1 hash of the file
    char hash[HASH_SIZE + 1];
    compute_sha1(filename, hash);

    // Create the root directory if it does not exist
    if (mkdir(root_dir, 0755) != 0 && errno != EEXIST) {
        return -1;
    }
    // Create the directory structure based on the first two characters of the hash
    char dir_name[PATH_MAX];
    strncpy(dir_name, root_dir, PATH_MAX - 1);
    dir_name[PATH_MAX - 1] = '\0';  // Ensure null-termination
    strncat(dir_name, "/", PATH_MAX - strlen(dir_name) - 1);
    strncat(dir_name, hash, 2);  // Only append the first two characters of the hash
    if (mkdir(dir_name, 0755) != 0 && errno != EEXIST) {
        return -1;
    }

    // Construct the file path using the hash
    char file_path[PATH_MAX];
    strncpy(file_path, dir_name, PATH_MAX - 1);
    file_path[PATH_MAX - 1] = '\0';  // Ensure null-termination
    strncat(file_path, "/", PATH_MAX - strlen(file_path) - 1);
    strncat(file_path, hash, PATH_MAX - strlen(file_path) - 1);

    // Check if the file already exists
    struct stat file_stat;
    if (stat(file_path, &file_stat) == 0) {
        return 0; // File already exists, success
    }
    // Copy the file to the new location
    if (copy_file(filename, file_path) != 0) {
            // TODO: #22 also delete the file if it exists
        return -1; // Indicate failure
    }
}
