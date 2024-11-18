#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include "utils.h"

int create_directory(const char *dir_name)
{
    if (mkdir(dir_name, 0755) == -1 && errno != EEXIST)
    {
        perror("Failed to create directory");
        return 0;
    }
    return 1;
}

int file_exists(const char *file_path)
{
    struct stat file_stat;
    return stat(file_path, &file_stat) == 0;
}

int copy_file(const char *src, const char *dest)
{
    FILE *source_file = fopen(src, "rb");
    if (!source_file)
    {
        perror("Failed to open source file");
        return 0;
    }

    FILE *dest_file = fopen(dest, "wb");
    if (!dest_file)
    {
        perror("Failed to create destination file");
        fclose(source_file);
        return 0;
    }

    unsigned char buffer[BUFFER_SIZE];
    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, source_file)) > 0)
    {
        fwrite(buffer, 1, bytes_read, dest_file);
        if (ferror(dest_file))
        {
            perror("Error writing to destination file");
            fclose(source_file);
            fclose(dest_file);
            return 0;
        }
    }
    fclose(source_file);
    fclose(dest_file);
    return 1;
}

int remove_file(const char *file_path)
{
    if (remove(file_path) == 0)
    {
        printf("Deleted: %s\n", file_path);
        return 1;
    }
    perror("Error deleting file");
    return 0;
}

void delete_empty_directory(const char *dir_name)
{
    if (rmdir(dir_name) == 0)
    {
        printf("Directory %s is now empty and deleted.\n", dir_name);
    }
    else
    {
        perror("Error deleting directory");
    }
}
