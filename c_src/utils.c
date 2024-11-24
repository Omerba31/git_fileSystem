#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/types.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include "file_utils.h"

int copy_file(const char *src, const char *dest)
{
    FILE *source_file = fopen(src, "rb");
    if (!source_file)
    {
        return 0;
    }

    FILE *dest_file = fopen(dest, "wb");
    if (!dest_file)
    {
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
    // Check if the file exists before attempting removal (➕)
    if (access(file_path, F_OK) != 0)
    {
        return -1;
    }

    if (remove(file_path) == 0)
    {
        return 0;
    }

    return -1;
}

int delete_empty_directory(const char *dir_name)
{
    if (rmdir(dir_name) == EXIT_SUCCESS)
    {
        return EXIT_SUCCESS;
    }
    else
    {
        return EXIT_FAILURE;
    }
}
