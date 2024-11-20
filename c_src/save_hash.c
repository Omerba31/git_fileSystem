#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include "save_hash.h"
#include "utils.h"

void save_file_based_on_hash(const char *filename, const char *hash) {
    // Create the hashed_files directory in the current directory
    const char *root_dir = "./hashed_files";
    create_directory(root_dir);

    // Create the directory structure based on the first two characters of the hash
    char dir_name[256];
    snprintf(dir_name, sizeof(dir_name), "%s/%.2s", root_dir, hash);
    create_directory(dir_name);

    // Construct the file path using the hash
    size_t file_path_size = strlen(dir_name) + 1 + strlen(hash) + 1;
    char *file_path = malloc(file_path_size);
    if (!file_path) {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }
    snprintf(file_path, file_path_size, "%s/%s", dir_name, hash);

    if (file_exists(file_path)) {
        printf("File already exists in the system: %s\n", file_path);
        free(file_path);
        return;
    }

    copy_file(filename, file_path);
    printf("File saved as %s\n", file_path);
    free(file_path);
}
