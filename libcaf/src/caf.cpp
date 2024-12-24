#include "caf.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <linux/limits.h>
#include <sys/file.h>
#include <openssl/evp.h>
#include <time.h>
#include <tuple>
#include <iostream>

#define BUFFER_SIZE 4096
#define DIR_NAME_SIZE 2

int compute_hash(const char *filename, char *output){
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    unsigned char buffer[BUFFER_SIZE];

    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (!mdctx){
        return -1;
    }
    if (EVP_DigestInit_ex(mdctx, EVP_sha1(), nullptr) != 1){
        EVP_MD_CTX_free(mdctx);
        return -1;
    }

    FILE *file = fopen(filename, "rb");
    if (!file){
        EVP_MD_CTX_free(mdctx);
        return -1;
    }

    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, file)) > 0){
        if (EVP_DigestUpdate(mdctx, buffer, bytes_read) != 1){
            fclose(file);
            EVP_MD_CTX_free(mdctx);
            return -1;
        }
    }
    fclose(file);

    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1){
        EVP_MD_CTX_free(mdctx);
        return -1;
    }

    for (unsigned int i = 0; i < hash_len; i++){
        sprintf(output + (i * 2), "%02x", hash[i]);
    }
    output[hash_len * 2] = '\0';
    EVP_MD_CTX_free(mdctx);
    return 0;
}

int compute_hash(const std::string& input, std::string& output) {
    unsigned char hash[HASH_SIZE + 1] = {0};
    EVP_MD_CTX* mdctx = EVP_MD_CTX_new();
    if (mdctx == nullptr) {
        return -1;
    }

    if (EVP_DigestInit_ex(mdctx, EVP_sha1(), nullptr) != 1) {
        EVP_MD_CTX_free(mdctx);
        return -1;
    }

    if (EVP_DigestUpdate(mdctx, input.c_str(), input.size()) != 1) {
        EVP_MD_CTX_free(mdctx);
        return -1;
    }

    unsigned int hash_len;
    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1) {
        EVP_MD_CTX_free(mdctx);
        return -1;
    }

    char buf[HASH_SIZE + 1 + 1];
    buf[HASH_SIZE + 1] = 0;
    for (unsigned int i = 0; i < hash_len; i++) {
        snprintf(buf + i * 2, 3, "%02x", hash[i]);
    }
    output = std::string(buf);
    EVP_MD_CTX_free(mdctx);

    return 0;
}

int save_content(const char *root_dir, const char *filename){
    if (mkdir(root_dir, 0755) != 0 && errno != EEXIST)
        return -1;

    char hash[HASH_SIZE + 1];
    if (compute_hash(filename, hash) != 0)
        return -1;

    char content_path[PATH_MAX];
    if (create_content_path(root_dir, hash, content_path, sizeof(content_path)) != 0)
        return -1;

    int fd = open(content_path, O_WRONLY | O_CREAT, 0644);
    if (fd < 0)
    {
        return -1;
    }

    if (lock_file_with_timeout(fd, LOCK_EX, 10) != 0)
    {
        close(fd);
        return -1;
    }

    if (copy_file(filename, content_path) != 0)
    {
        flock(fd, LOCK_UN);
        close(fd);
        unlink(content_path);
        return -1;
    }

    flock(fd, LOCK_UN);
    close(fd);
    return 0;
}

std::tuple<int, int, std::string> save_content(const std::string &root_dir, const std::string &hash, int flags) {
    // Ensure the root directory exists
    if (mkdir(root_dir.c_str(), 0755) != 0 && errno != EEXIST) {
        return {-1, -1, ""};  // Failed to create root directory
    }

    // Generate the blob path using the hash
    char content_path[PATH_MAX];
    if (create_content_path(root_dir.c_str(), hash.c_str(), content_path, sizeof(content_path)) != 0) {
        return {-1, -1, ""};  // Failed to generate content path
    }

    // Open the file with specified flags
    int fd = open(content_path, flags, 0644);  // Use specified flags and permissions
    if (fd < 0) {
            std::cerr << "Failed to open file: " << content_path
              << ", errno: " << strerror(errno) << std::endl;
        return {-1, -1, ""};  // Failed to open file
    }

    // Lock the file with a timeout
    if (lock_file_with_timeout(fd, LOCK_EX, 10) != 0) {  // Exclusive lock with a 10-second timeout
        close(fd);  // Close the file on failure
        return {-1, -1, ""};
    }

    return {0, fd, std::string(content_path)};  // Success: return result, file descriptor, and blob path
}

int delete_content(const char *root_dir, const char *hash){
    char content_path[PATH_MAX];
    if (create_content_path(root_dir, hash, content_path, sizeof(content_path)) != 0)
        return -1;

    int fd = open(content_path, O_RDONLY);
    if (fd < 0)
    {
        if (errno == ENOENT)
            return 0;
        return -1;
    }

    if (flock(fd, LOCK_SH | LOCK_NB) != 0)
    {
        if (errno == EWOULDBLOCK)
        {
            close(fd);
            return -1;
        }
        close(fd);
        return -1;
    }

    flock(fd, LOCK_UN);
    close(fd);

    if (unlink(content_path) != 0)
        return -1;

    char dir_path[PATH_MAX];
    snprintf(dir_path, sizeof(dir_path), "%s/%c%c", root_dir, hash[0], hash[1]);
    if (rmdir(dir_path) != 0 && errno != ENOTEMPTY)
        return -1;

    return 0;
}

int open_content(const char *root_dir, const char *hash){
    char content_path[PATH_MAX];
    if (create_content_path(root_dir, hash, content_path, sizeof(content_path)) != 0)
        return -1;

    int fd = open(content_path, O_RDONLY);
    if (fd < 0)
    {
        if (errno == ENOENT)
            return -1;
        return -1;
    }

    if (lock_file_with_timeout(fd, LOCK_SH, 10) != 0) // 10-second timeout
    {
        close(fd);
        return -1;
    }

    return fd;
}

int copy_file(const char *src, const char *dest){
    FILE *source_file = fopen(src, "rb");
    if (!source_file)
        return -1;

    FILE *dest_file = fopen(dest, "wb");
    if (!dest_file)
    {
        fclose(source_file);
        return -1;
    }

    unsigned char buffer[BUFFER_SIZE];
    size_t bytes_read;

    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, source_file)) > 0)
    {
        if (fwrite(buffer, 1, bytes_read, dest_file) != bytes_read)
        {
            fclose(source_file);
            fclose(dest_file);
            return -1;
        }

        if (ferror(dest_file))
        {
            fclose(source_file);
            fclose(dest_file);
            return -1;
        }
    }
    fclose(source_file);
    fclose(dest_file);
    return 0;
}

int create_content_path(const char *root_dir, const char *hash, char *output_path, size_t output_size){
    if (!root_dir || !hash || !output_path)
        return -1;

    if (create_sub_dir(root_dir, hash) != 0)
        return -1;

    int i = snprintf(output_path, output_size, "%s/%c%c/%s", root_dir, hash[0], hash[1], hash);
    if (i < 0 || (size_t)i >= output_size)
        return -1;

    return 0;
}

int create_sub_dir(const char *root_dir, const char *hash){
    char sub_dir[3] = {hash[0], hash[1], '\0'};
    char sub_dir_path[PATH_MAX];
    int i = snprintf(sub_dir_path, sizeof(sub_dir_path), "%s/%s", root_dir, sub_dir);
    if (i < 0 || (size_t)i >= sizeof(sub_dir_path))
        return -1;

    if (mkdir(sub_dir_path, 0755) != 0 && errno != EEXIST)
        return -1;

    return 0;
}

int lock_file_with_timeout(int fd, int operation, int timeout_sec){
    time_t start_time = time(nullptr);

    while (flock(fd, operation | LOCK_NB) != 0)
    {
        if (errno == EWOULDBLOCK)
        {
            if (time(nullptr) - start_time >= timeout_sec)
            {
                printf("Lock attempt timed out after %d seconds.\n", timeout_sec);
                return -1; // Timeout reached
            }
            sleep(1); // Wait before retrying
        }
        else
        {
            perror("Error while acquiring lock");
            return -1;
        }
    }

    return 0;
}