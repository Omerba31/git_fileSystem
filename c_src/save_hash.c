#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include "save_hash.h"
#include "utils.h"

void save_file_based_on_hash(const char *filename, const char *hash)
{
    char dir_name[3];
    snprintf(dir_name, sizeof(dir_name), "%c%c", hash[0], hash[1]);

    create_directory(dir_name);

    size_t file_path_size = strlen(dir_name) + strlen(hash) + 2;
    char *file_path = malloc(file_path_size);
    if (!file_path)
    {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }
    snprintf(file_path, file_path_size, "%s/%s", dir_name, hash);

    if (file_exists(file_path))
    {
        printf("File already exists in the system: %s\n", file_path);
        free(file_path);
        return;
    }

    if (copy_file(filename, file_path))
    {
        printf("File saved as %s\n", file_path);
    }
    free(file_path);
}
