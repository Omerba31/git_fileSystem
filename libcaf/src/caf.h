#ifndef CAF_H
#define CAF_H

#include <unistd.h>
#include <string>
#include <cstddef>

#define HASH_SIZE 40

std::string hash_file(const std::string& file_path);
std::string hash_string(const std::string& content);
void save_file_content(const std::string& content_root_dir, const std::string& file_path);
int open_fd_for_saving_content(const std::string& content_root_dir, const std::string& content_hash);
void delete_content(const std::string& content_root_dir, const std::string& content_hash);
int open_fd_for_reading_content(const std::string& content_root_dir, const std::string& content_hash);
void close_content_fd(const int content_fd);

#endif // CAF_H