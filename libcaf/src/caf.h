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
int lock_file_with_timeout(int fd, int operation, int timeout_sec);
int create_sub_dir(const std::string& content_root_dir, const std::string& hash);
int create_content_path(const std::string& content_root_dir, const std::string& hash, char* output_path, size_t output_size);
int copy_file(const std::string& src, const std::string& dest);


#endif // CAF_H