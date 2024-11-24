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

int delete_file_based_on_hash(const char *root_dir, const char *hash){
    char file_path[PATH_MAX];
    int i = 0;

    // Copy the root directory path
    while (root_dir[i] != '\0') {
        file_path[i] = root_dir[i];
        PATH_ADVANCE(i);
    }

    // Ensure the root directory path ends with a '/'
    if (file_path[i - 1] != '/') {
        file_path[i] = '/';
        PATH_ADVANCE(i);
    }

    // Add the first DIR_NAME_SIZE characters of the hash to the directory path
    for (int j = 0; j < DIR_NAME_SIZE; j++) {
        file_path[i] = hash[j];
        PATH_ADVANCE(i);
    }
    file_path[i] = '/';
    PATH_ADVANCE(i);

    // Add the full hash to the file path
    for (int j = 0; j < HASH_SIZE && hash[j] != '\0'; j++) {
        file_path[i] = hash[j];
        PATH_ADVANCE(i);
    }

    // Null-terminate the file path
    file_path[i] = '\0';

    // Attempt to delete the file.
    if (unlink(file_path) != 0){
        return -1;
    }

    // Attempt to delete the containing directory (if empty)
    file_path[i - HASH_SIZE - 1] = '\0';
    if (rmdir(file_path) != 0) {
        if (errno != ENOTEMPTY) {
            return -1;
        }
    }
    return 0;
}
