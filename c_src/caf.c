#include "caf.h"

int compute_sha1(const char *filename, char *output)
{
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    unsigned char buffer[BUFFER_SIZE];

    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (!mdctx)
    {
        perror("Failed to create EVP_MD_CTX");
        return -1;
    }
    if (EVP_DigestInit_ex(mdctx, EVP_sha1(), NULL) != 1)
    {
        perror("EVP_DigestInit_ex failed");
        EVP_MD_CTX_free(mdctx);
        return -1;
    }

    // Add filename to the hash input
    if (EVP_DigestUpdate(mdctx, filename, strlen(filename)) != 1)
    {
        perror("EVP_DigestUpdate failed on filename");
        EVP_MD_CTX_free(mdctx);
        return -1;
    }

    FILE *file = fopen(filename, "rb");
    if (!file)
    {
        perror("Failed to open file");
        EVP_MD_CTX_free(mdctx);
        return -1;
    }

    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, file)) > 0)
    {
        if (EVP_DigestUpdate(mdctx, buffer, bytes_read) != 1)
        {
            perror("EVP_DigestUpdate failed on file content");
            fclose(file);
            EVP_MD_CTX_free(mdctx);
            return -1;
        }
    }
    fclose(file);

    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1)
    {
        perror("EVP_DigestFinal_ex failed");
        EVP_MD_CTX_free(mdctx);
        return -1;
    }

    for (unsigned int i = 0; i < hash_len; i++)
    {
        sprintf(output + (i * 2), "%02x", hash[i]);
    }
    output[hash_len * 2] = '\0';
    EVP_MD_CTX_free(mdctx);
    return 0;
}

int save_file(const char *root_dir, const char *filename)
{
    if (mkdir(root_dir, 0755) != 0 && errno != EEXIST)
        return -1;

    char hash[HASH_SIZE + 1];
    if (compute_sha1(filename, hash) != 0)
        return -1;

    char file_path[PATH_MAX];
    if (create_file_path(root_dir, hash, file_path, sizeof(file_path)) != 0)
        return -1;

    int fd = open(file_path, O_WRONLY | O_CREAT, 0644);
    if (fd < 0)
    {
        perror("Failed to create file");
        return -1;
    }

    if (lock_file_with_timeout(fd, LOCK_EX, 10) != 0)
    {
        close(fd);
        return -1;
    }

    if (copy_file(filename, file_path) != 0)
    {
        flock(fd, LOCK_UN);
        close(fd);
        unlink(file_path);
        return -1;
    }

    flock(fd, LOCK_UN);
    close(fd);
    return 0;
}

int delete_file(const char *root_dir, const char *hash)
{
    char file_path[PATH_MAX];
    if (create_file_path(root_dir, hash, file_path, sizeof(file_path)) != 0)
        return -1;

    int fd = open(file_path, O_RDONLY);
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
        perror("Failed to acquire shared lock");
        close(fd);
        return -1;
    }

    flock(fd, LOCK_UN);
    close(fd);

    if (unlink(file_path) != 0)
        return -1;

    char dir_path[PATH_MAX];
    snprintf(dir_path, sizeof(dir_path), "%s/%c%c", root_dir, hash[0], hash[1]);
    if (rmdir(dir_path) != 0 && errno != ENOTEMPTY)
        return -1;

    return 0;
}

int open_file(const char *root_dir, const char *hash)
{
    char file_path[PATH_MAX];
    if (create_file_path(root_dir, hash, file_path, sizeof(file_path)) != 0)
        return -1;

    int fd = open(file_path, O_RDONLY);
    if (fd < 0)
    {
        if (errno == ENOENT)
            return -1;
        perror("Failed to open file");
        return -1;
    }

    if (lock_file_with_timeout(fd, LOCK_SH, 10) != 0) // 10-second timeout
    {
        close(fd);
        return -1;
    }

    return fd;
}

int copy_file(const char *src, const char *dest)
{
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

int create_file_path(const char *root_dir, const char *hash, char *output_path, size_t output_size)
{
    if (!root_dir || !hash || !output_path)
        return -1;

    if (create_sub_dir(root_dir, hash) != 0)
        return -1;

    int i = snprintf(output_path, output_size, "%s/%c%c/%s", root_dir, hash[0], hash[1], hash);
    if (i < 0 || (size_t)i >= output_size)
        return -1;

    return 0;
}

int create_sub_dir(const char *root_dir, const char *hash)
{
    char sub_dir[3] = {hash[0], hash[1], '\0'};
    char sub_dir_path[PATH_MAX];
    int i = snprintf(sub_dir_path, sizeof(sub_dir_path), "%s/%s", root_dir, sub_dir);
    if (i < 0 || (size_t)i >= sizeof(sub_dir_path))
        return -1;

    if (mkdir(sub_dir_path, 0755) != 0 && errno != EEXIST)
        return -1;

    return 0;
}

int lock_file_with_timeout(int fd, int operation, int timeout_sec)
{
    time_t start_time = time(NULL);

    while (flock(fd, operation | LOCK_NB) != 0)
    {
        if (errno == EWOULDBLOCK)
        {
            if (time(NULL) - start_time >= timeout_sec)
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
