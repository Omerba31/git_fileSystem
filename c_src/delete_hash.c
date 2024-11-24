#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "file_utils.h"

void delete_file_based_on_hash(const char *hash)
{
    //  TODO: chnge root dir to be function parameter and check pytests working. (like in openfile)
    const char *root_dir = "./objects"; // Added root directory definition (➕)
    char dir_name[3];
    snprintf(dir_name, sizeof(dir_name), "%c%c", hash[0], hash[1]);

    size_t file_path_size = strlen(root_dir) + strlen(dir_name) + strlen(hash) + 3;
    // TODO :  check with we can remove malloc
    char *file_path = malloc(file_path_size);
    if (!file_path)
    {
        return;
    }

    size_t dir_path_size = strlen(root_dir) + strlen(dir_name) + 2; // One '/' and null terminator (➕)
    char *dir_path = malloc(dir_path_size);                         // Allocate memory for full directory path (➕)
    if (!dir_path)                                                  // Check allocation (➕)
    {
        free(file_path);                                 // Free previously allocated file_path (➕)
        return;
    }

    snprintf(file_path, file_path_size, "%s/%s/%s", root_dir, dir_name, hash);
    snprintf(dir_path, dir_path_size, "%s/%s", root_dir, dir_name);

    if (remove_file(file_path) == 0)
    {
        if (delete_empty_directory(dir_path) == 0)
        {
            printf("Directory deleted successfully: %s\n", dir_path);
        }
    }

    free(dir_path);
    free(file_path); 
}
