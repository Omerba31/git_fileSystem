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

std::string hash_file(const std::string& filename){
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    unsigned char buffer[BUFFER_SIZE];

    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (!mdctx){
        throw std::runtime_error("Failed to create EVP_MD_CTX");
    }

    if (EVP_DigestInit_ex(mdctx, EVP_sha1(), nullptr) != 1){
        EVP_MD_CTX_free(mdctx);
        throw std::runtime_error("Failed to initialize digest");
    }

    FILE *file = fopen(filename.c_str(), "rb");
    if (!file){
        EVP_MD_CTX_free(mdctx);
        throw std::runtime_error("Failed to open file");
    }

    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, file)) > 0){
        if (EVP_DigestUpdate(mdctx, buffer, bytes_read) != 1){
            fclose(file);
            EVP_MD_CTX_free(mdctx);
            throw std::runtime_error("Failed to update digest");
        }
    }

    fclose(file);

    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1){
        EVP_MD_CTX_free(mdctx);
        throw std::runtime_error("Failed to finalize digest");
    }

    EVP_MD_CTX_free(mdctx);

    std::string output;
    output.reserve(hash_len * 2);
    for (unsigned int i = 0; i < hash_len; ++i) {
        char hex[3];
        sprintf(hex, "%02x", hash[i]);
        output.append(hex);
    }

    return output;
}

std::string hash_string(const std::string& content){
    unsigned char hash[HASH_SIZE + 1] = {0};
    EVP_MD_CTX* mdctx = EVP_MD_CTX_new();

    if (mdctx == nullptr) {
        throw std::runtime_error("Failed to create EVP_MD_CTX");
    }

    if (EVP_DigestInit_ex(mdctx, EVP_sha1(), nullptr) != 1) {
        EVP_MD_CTX_free(mdctx);
        throw std::runtime_error("Failed to initialize digest");
    }

    if (EVP_DigestUpdate(mdctx, content.c_str(), content.size()) != 1) {
        EVP_MD_CTX_free(mdctx);
        throw std::runtime_error("Failed to update digest");
    }

    unsigned int hash_len;
    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1) {
        EVP_MD_CTX_free(mdctx);
        throw std::runtime_error("Failed to finalize digest");
    }

    EVP_MD_CTX_free(mdctx);

    std::string output;
    output.reserve(hash_len * 2);
    for (unsigned int i = 0; i < hash_len; ++i) {
        char hex[3];
        snprintf(hex, sizeof(hex), "%02x", hash[i]);
        output.append(hex);
    }

    return output;
}

void save_file_content(const std::string& content_root_dir, const std::string& file_path){
    if (mkdir(content_root_dir.c_str(), 0755) != 0 && errno != EEXIST)
        throw std::runtime_error("Failed to create root directory");

    std::string file_hash = hash_file(file_path);
    if (file_hash.empty())
        throw std::runtime_error("Failed to compute hash");

    char content_path[PATH_MAX];
    if (create_content_path(content_root_dir.c_str(), file_hash, content_path, sizeof(content_path)) != 0)
        throw std::runtime_error("Failed to create content path");

    int fd = open(content_path, O_WRONLY | O_CREAT, 0644);
    if (fd < 0)
    {
        throw std::runtime_error("Failed to open file");
    }

    if (lock_file_with_timeout(fd, LOCK_EX, 10) != 0)
    {
        close(fd);
        throw std::runtime_error("Failed to lock file");
    }

    if (copy_file(file_path, content_path) != 0)
    {
        flock(fd, LOCK_UN);
        close(fd);
        unlink(content_path);
        throw std::runtime_error("Failed to copy file");
    }

    flock(fd, LOCK_UN);
    close(fd);
}

int open_fd_for_saving_content(const std::string& content_root_dir, const std::string& content_hash){
    if (mkdir(content_root_dir.c_str(), 0755) != 0 && errno != EEXIST) {
        return -1;
    }

    char content_path[PATH_MAX];
    if (create_content_path(content_root_dir.c_str(), content_hash.c_str(), content_path, sizeof(content_path)) != 0) {
        return -1;
    }

    int fd = open(content_path, O_WRONLY|O_CREAT, 0644);
    if (fd < 0) {
        return -1;
    }

    if (lock_file_with_timeout(fd, LOCK_EX, 10) != 0) {
        close(fd);
        return -1;;
    }

    return fd;
}

void delete_content(const std::string& content_root_dir, const std::string& content_hash){
    char content_path[PATH_MAX];
    if (create_content_path(content_root_dir.c_str(), content_hash.c_str(), content_path, sizeof(content_path)) != 0)
        throw std::runtime_error("Failed to create content path");

    int fd = open(content_path, O_RDONLY);
    if (fd < 0)
    {
        if (errno == ENOENT)
            return;
        throw std::runtime_error("Failed to open file");
    }

    if (flock(fd, LOCK_SH | LOCK_NB) != 0)
    {
        if (errno == EWOULDBLOCK)
        {
            close(fd);
            throw std::runtime_error("File is currently locked by another process");
        }
        close(fd);
        throw std::runtime_error("Failed to lock file");
    }

    flock(fd, LOCK_UN);
    close(fd);

    if (unlink(content_path) != 0)
        throw std::runtime_error("Failed to delete file");

    char dir_path[PATH_MAX];
    snprintf(dir_path, sizeof(dir_path), "%s/%c%c", content_root_dir.c_str(), content_hash[0], content_hash[1]);
    if (rmdir(dir_path) != 0 && errno != ENOTEMPTY)
        throw std::runtime_error("Failed to delete directory");
}

int open_fd_for_reading_content(const std::string& content_root_dir, const std::string& content_hash){
    char content_path[PATH_MAX];
    if (create_content_path(content_root_dir.c_str(), content_hash.c_str(), content_path, sizeof(content_path)) != 0)
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

int copy_file(const std::string& src, const std::string& dest) {
    FILE* source_file = fopen(src.c_str(), "rb");
    if (!source_file)
        return -1;

    FILE *dest_file = fopen(dest.c_str(), "wb");
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

int create_content_path(const std::string& content_root_dir, const std::string& hash, char* output_path, size_t output_size) {
    if (content_root_dir.empty() || hash.empty() || !output_path)
        return -1;

    if (create_sub_dir(content_root_dir, hash) != 0)
        return -1;

    int i = snprintf(output_path, output_size, "%s/%c%c/%s", content_root_dir.c_str(), hash[0], hash[1], hash.c_str());
    if (i < 0 || (size_t)i >= output_size)
        return -1;

    return 0;
}

int create_sub_dir(const std::string& content_root_dir, const std::string& hash) {
    if (content_root_dir.empty() || hash.length() < 2)
        return -1;

    std::string sub_dir_path = content_root_dir + "/" + hash.substr(0, 2);

    if (mkdir(sub_dir_path.c_str(), 0755) != 0 && errno != EEXIST)
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