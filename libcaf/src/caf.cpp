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

std::string create_sub_dir(const std::string& content_root_dir, const std::string& hash);
void lock_file_with_timeout(int fd, int operation, int timeout_sec);
void copy_file(const std::string& src, const std::string& dest);
void create_content_path(const std::string& content_root_dir, const std::string& hash, std::string& output_path, size_t output_size);

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

Blob save_file_content(const std::string& content_root_dir, const std::string& file_path){
    if (mkdir(content_root_dir.c_str(), 0755) != 0 && errno != EEXIST)
        throw std::runtime_error("Failed to create root directory");

    std::string file_hash = hash_file(file_path);

    std::string content_path;
    create_content_path(content_root_dir, file_hash, content_path, sizeof(content_path));

    int fd = open(content_path.c_str(), O_WRONLY | O_CREAT, 0644);

    if (fd < 0)
        throw std::runtime_error("Failed to open file");

    try{
        lock_file_with_timeout(fd, LOCK_EX, 10);
    } catch (const std::exception& e){
        close(fd);
        throw;
    }

    try {
        copy_file(file_path, content_path);
    } catch (const std::exception& e) {
        unlink(content_path.c_str());
        flock(fd, LOCK_UN);
        close(fd);
        throw;
    }

    flock(fd, LOCK_UN);
    close(fd);

    return Blob(file_hash);
}

int open_content_for_saving(const std::string& content_root_dir, const std::string& content_hash){
    if (mkdir(content_root_dir.c_str(), 0755) != 0 && errno != EEXIST) {
        throw std::runtime_error("Failed to create root directory");
    }

    std::string content_path;
    create_content_path(content_root_dir, content_hash, content_path, sizeof(content_path));

    int fd = open(content_path.c_str(), O_WRONLY|O_CREAT, 0644);

    if (fd < 0) {
        throw std::runtime_error("Failed to open file");
    }

    try{
        lock_file_with_timeout(fd, LOCK_EX, 10);
    } catch (const std::exception& e){
        close(fd);
        throw;
    }

    return fd;
}

void delete_content(const std::string& content_root_dir, const std::string& content_hash) {
    std::string content_path;
    create_content_path(content_root_dir, content_hash, content_path, sizeof(content_path));

    int fd = open(content_path.c_str(), O_RDONLY);
    if (fd < 0)
    {
        if (errno == ENOENT)
            return;
        throw std::runtime_error("Failed to open file");
    }

    try{
            lock_file_with_timeout(fd, LOCK_EX, 10);
        } catch (const std::exception& e){
            close(fd);
            throw;
        }

    if (unlink(content_path.c_str()) != 0)
        throw std::runtime_error("Failed to delete file");

    flock(fd, LOCK_UN);
    close(fd);
}

int open_content_for_reading(const std::string& content_root_dir, const std::string& content_hash){
    std::string content_path;
    create_content_path(content_root_dir, content_hash, content_path, sizeof(content_path));

    int fd = open(content_path.c_str(), O_RDONLY);

    if (fd < 0)
        throw std::runtime_error("Failed to open file");

    try{
        lock_file_with_timeout(fd, LOCK_EX, 10);
    } catch (const std::exception& e){
        close(fd);
        throw;
    }

    return fd;
}

void copy_file(const std::string& src, const std::string& dest) {
    FILE* source_file = fopen(src.c_str(), "rb");
    if (!source_file)
        throw std::runtime_error("Failed to open source file");

    FILE *dest_file = fopen(dest.c_str(), "wb");
    if (!dest_file)
    {
        fclose(source_file);
        throw std::runtime_error("Failed to open destination file");
    }

    unsigned char buffer[BUFFER_SIZE];
    size_t bytes_read;

    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, source_file)) > 0)
    {
        if (fwrite(buffer, 1, bytes_read, dest_file) != bytes_read)
        {
            fclose(source_file);
            fclose(dest_file);
            throw std::runtime_error("Failed to write to destination file");
        }

        if (ferror(dest_file))
        {
            fclose(source_file);
            fclose(dest_file);
            throw std::runtime_error("Error while writing to destination file");
        }
    }
    fclose(source_file);
    fclose(dest_file);
}

void create_content_path(const std::string& content_root_dir, const std::string& hash, std::string& output_path, size_t output_size) {
    if (content_root_dir.empty() || hash.empty())
        throw std::invalid_argument("Invalid argument");

    output_path = create_sub_dir(content_root_dir, hash) + "/" + hash;
}

std::string create_sub_dir(const std::string& content_root_dir, const std::string& hash) {
    if (content_root_dir.empty() || hash.length() < 2)
        throw std::invalid_argument("Invalid argument");

    std::string sub_dir_path = content_root_dir + "/" + hash.substr(0, 2);

    if (mkdir(sub_dir_path.c_str(), 0755) != 0 && errno != EEXIST)
        throw std::runtime_error("Failed to create sub directory");

    return sub_dir_path;
}

void lock_file_with_timeout(int fd, int operation, int timeout_sec){
    time_t start_time = time(nullptr);

    while (flock(fd, operation | LOCK_NB) != 0)
    {
        if (errno == EWOULDBLOCK)
        {
            if (time(nullptr) - start_time >= timeout_sec)
                throw std::runtime_error("Failed to acquire lock");
            sleep(1);
        }
        else
            throw std::runtime_error("Failed to acquire lock");
    }
}
