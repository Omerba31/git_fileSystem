#include "open_file.h"
#include "sha1_utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#define HASH_SIZE 40     // SHA-1 hash size (in characters)
#define BUFFER_SIZE 4096 // Buffer size for file operations

// Function to find and open the file based on its hash (file name is hashed)
int open_file_by_hash(const char *filename) {
    char hash[HASH_SIZE + 1];
    compute_sha1(filename, hash);
    
    // Create the directory structure based on the first two characters of the hash
    char dir_name[3]; // First two characters of the hash
    snprintf(dir_name, sizeof(dir_name), "%c%c", hash[0], hash[1]);

    // Construct the file path using the hash and the ./hashed_files directory
    char file_path[256];
    snprintf(file_path, sizeof(file_path), "./hashed_files/%s/%s", dir_name, hash);

    printf("Computed hash: %s\n", hash);
    printf("Constructed file path: %s\n", file_path);

    // Open the file and return the file descriptor
    int fd = open(file_path, O_RDONLY);
    if (fd == -1) {
        perror("Failed to open file");
        return -1; // Return -1 if the file cannot be opened
    }
    printf("fd-1: %d\n", fd);

    return fd;
}

