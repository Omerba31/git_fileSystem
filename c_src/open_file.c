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


// Function to open the file based on its hash
int open_content(const char *root_dir, const char *hash) {
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

    // Copy the first DIR_NAME_SIZE characters of the hash
    for (int j = 0; j < DIR_NAME_SIZE; j++) {
        file_path[i] = hash[j];
        PATH_ADVANCE(i);
    }
    file_path[i] = '/';
    PATH_ADVANCE(i);

    // Copy exactly HASH_SIZE bytes from the hash
    for (int j = 0; j < HASH_SIZE && j < strlen(hash); j++) {
        file_path[i] = hash[j];
        PATH_ADVANCE(i);
    }

    // Null-terminate the file path
    file_path[i] = '\0';

    // Open the file and return the file descriptor
    int fd = open(file_path, O_RDONLY);

    return fd;
}
