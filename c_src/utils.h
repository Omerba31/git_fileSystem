#ifndef UTILS_H
#define UTILS_H

#define BUFFER_SIZE 4096

int create_directory(const char *dir_name);
int file_exists(const char *file_path);
int copy_file(const char *src, const char *dest);
int remove_file(const char *file_path);
void delete_empty_directory(const char *dir_name);

#endif // UTILS_H
