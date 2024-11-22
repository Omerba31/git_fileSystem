#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "file_utils.h"

void delete_file_based_on_hash(const char *hash)
{
    char dir_name[3];
    snprintf(dir_name, sizeof(dir_name), "%c%c", hash[0], hash[1]);

    size_t file_path_size = strlen(dir_name) + strlen(hash) + 2;
    char *file_path = malloc(file_path_size);
    if (!file_path)
    {
        perror("Memory allocation failed");
        return;
    }
    snprintf(file_path, file_path_size, "%s/%s", dir_name, hash);

    if (remove_file(file_path))
    {
        delete_empty_directory(dir_name);
    }
    free(file_path);
}
