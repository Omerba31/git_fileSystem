#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

#define HASH_SIZE 40     // SHA-1 hash size (in characters)
#define BUFFER_SIZE 4096 // Buffer size for file operations

// Function declarations
void compute_sha1(const char *filename, char *output);
void save_file_based_on_hash(const char *filename, const char *hash);
void delete_file_based_on_hash(const char *hash);
void delete_file_based_on_hash_by_name(const char *hash);
void delete_file_by_name(const char *filename);
void remove_file_using_filePath(char *file_path, int *retFlag);
void delete_directory_if_empty(char dir_name[3], char *file_path);

// Function to compute SHA-1 hash of a file (filename + content)
void compute_sha1(const char *filename, char *output)
{
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    unsigned char buffer[BUFFER_SIZE];

    // Create and initialize the digest context
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (!mdctx)
    {
        perror("Failed to create EVP_MD_CTX");
        exit(EXIT_FAILURE);
    }
    if (EVP_DigestInit_ex(mdctx, EVP_sha1(), NULL) != 1)
    {
        perror("EVP_DigestInit_ex failed");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    // Hash the filename
    if (EVP_DigestUpdate(mdctx, filename, strlen(filename)) != 1)
    {
        perror("EVP_DigestUpdate failed on filename");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    // Open the file to hash its content
    FILE *file = fopen(filename, "rb");
    if (!file)
    {
        perror("Failed to open file");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    // Read and hash the file content
    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, file)) > 0)
    {
        if (EVP_DigestUpdate(mdctx, buffer, bytes_read) != 1)
        {
            perror("EVP_DigestUpdate failed on file content");
            fclose(file);
            EVP_MD_CTX_free(mdctx);
            exit(EXIT_FAILURE);
        }
    }
    fclose(file);

    // Finalize the hash computation
    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1)
    {
        perror("EVP_DigestFinal_ex failed");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    // Convert hash to hexadecimal string
    for (unsigned int i = 0; i < hash_len; i++)
    {
        sprintf(output + (i * 2), "%02x", hash[i]);
    }
    output[hash_len * 2] = '\0'; // Null-terminate the hash string

    EVP_MD_CTX_free(mdctx);
}

// Function to save a file in a directory structure based on its hash
void save_file_based_on_hash(const char *filename, const char *hash)
{
    char dir_name[3]; // Directory name derived from the first two characters of the hash
    snprintf(dir_name, sizeof(dir_name), "%c%c", hash[0], hash[1]);

    // Create the directory if it doesn't exist
    if (mkdir(dir_name, 0755) == -1 && errno != EEXIST)
    {
        perror("Failed to create directory");
        exit(EXIT_FAILURE);
    }

    // Build the full file path
    size_t file_path_size = strlen(dir_name) + strlen(hash) + 2; // 1 for '/' and 1 for '\0'
    char *file_path = malloc(file_path_size);
    if (!file_path)
    {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }
    snprintf(file_path, file_path_size, "%s/%s", dir_name, hash);

    // Check if the file already exists
    struct stat file_stat;
    if (stat(file_path, &file_stat) == 0)
    {
        printf("File already exists in the system: %s\n", file_path);
        free(file_path);
        return;
    }

    // Lock file to prevent concurrent writes
    char lock_file_path[file_path_size + 5]; // +5 for ".lock"
    snprintf(lock_file_path, sizeof(lock_file_path), "%s.lock", file_path);

    int lock_fd = open(lock_file_path, O_CREAT | O_EXCL, 0644);
    if (lock_fd == -1)
    {
        perror("Failed to create lock file");
        free(file_path);
        exit(EXIT_FAILURE);
    }

    // Open source and destination files
    FILE *source_file = fopen(filename, "rb");
    if (!source_file)
    {
        perror("Failed to open source file");
        close(lock_fd);
        unlink(lock_file_path);
        free(file_path);
        exit(EXIT_FAILURE);
    }

    FILE *dest_file = fopen(file_path, "wb");
    if (!dest_file)
    {
        perror("Failed to create destination file");
        fclose(source_file);
        close(lock_fd);
        unlink(lock_file_path);
        free(file_path);
        exit(EXIT_FAILURE);
    }

    // Copy content from source to destination
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
            close(lock_fd);
            unlink(lock_file_path);
            free(file_path);
            exit(EXIT_FAILURE);
        }
    }
    fclose(source_file);
    fclose(dest_file);
    close(lock_fd);
    unlink(lock_file_path); // Remove lock file
    printf("File saved as %s\n", file_path);
    free(file_path);
}

// Function to delete a file based on its hash
void delete_file_based_on_hash(const char *hash)
{
    char dir_name[3];
    snprintf(dir_name, sizeof(dir_name), "%c%c", hash[0], hash[1]);

    size_t file_path_size = strlen(dir_name) + strlen(hash) + 2;
    char *file_path = malloc(file_path_size);
    if (!file_path)
    {
        perror("Memory allocation failed");
        return;
    }
    snprintf(file_path, file_path_size, "%s/%s", dir_name, hash);

    int retFlag;
    remove_file_using_filePath(file_path, &retFlag);
    if (retFlag == 1)
    {
        free(file_path);
        return;
    }

    delete_directory_if_empty(dir_name, file_path);
    free(file_path);
}

// Helper function to remove a file by its file path
void remove_file_using_filePath(char *file_path, int *retFlag)
{
    *retFlag = 1;
    if (remove(file_path) == 0)
    {
        printf("Deleted: %s\n", file_path);
        *retFlag = 0;
    }
    else
    {
        perror("Error deleting file");
    }
}

// Helper function to delete a directory if empty
void delete_directory_if_empty(char dir_name[3], char *file_path)
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

int main(int argc, char *argv[])
{
    printf("=== File Storage System Tests ===\n");

    // Helper function: Clean up the environment
    void cleanup_test_environment(const char *hash)
    {
        // Delete the test file and any directories/files created
        remove("test_file.txt");
        if (hash)
            delete_file_based_on_hash(hash);
    }

    // Test 1: Compute SHA-1 hash
    printf("\n--- Test 1: Compute SHA-1 Hash ---\n");
    FILE *test_file = fopen("test_file.txt", "w");
    if (!test_file)
    {
        perror("Failed to create test file");
        return EXIT_FAILURE;
    }
    fprintf(test_file, "This is a test file.");
    fclose(test_file);

    char hash[HASH_SIZE + 1];
    compute_sha1("test_file.txt", hash);
    printf("Computed SHA-1 hash: %s\n", hash);

    // Test 2: Save file based on its hash
    printf("\n--- Test 2: Save File Based on Hash ---\n");
    save_file_based_on_hash("test_file.txt", hash);

    // Check if the file was saved correctly
    char dir_name[3];
    snprintf(dir_name, sizeof(dir_name), "%c%c", hash[0], hash[1]);
    char file_path[strlen(dir_name) + HASH_SIZE + 2];
    snprintf(file_path, sizeof(file_path), "%s/%s", dir_name, hash);

    if (access(file_path, F_OK) == 0)
    {
        printf("File successfully saved at: %s\n", file_path);
    }
    else
    {
        printf("Error: File was not saved correctly.\n");
    }

    // Test 3: Delete file based on its hash
    printf("\n--- Test 3: Delete File Based on Hash ---\n");
    delete_file_based_on_hash(hash);

    // Verify the file no longer exists
    if (access(file_path, F_OK) != 0)
    {
        printf("File successfully deleted: %s\n", file_path);
    }
    else
    {
        printf("Error: File was not deleted correctly.\n");
    }

    // Clean up test artifacts
    printf("\n--- Cleanup ---\n");
    cleanup_test_environment(hash);

    printf("\n=== Tests Completed ===\n");
    return EXIT_SUCCESS;
}
