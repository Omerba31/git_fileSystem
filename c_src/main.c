#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

#define HASH_SIZE 40
#define BUFFER_SIZE 4096

// Function declarations
void remove_file_using_filePath(char *file_path, int *retFlag);
void delete_directory_if_empty(char dir_name[3], char *file_path);

/*
// Function to compute SHA-1 hash of a file using EVP API
void compute_sha1(const char *filename, char *output)
{
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    unsigned char buffer[BUFFER_SIZE];
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (!mdctx)
    {
        perror("Failed to create EVP_MD_CTX");
        exit(EXIT_FAILURE);
    }

    // Initialize the digest context for SHA-1
    if (EVP_DigestInit_ex(mdctx, EVP_sha1(), NULL) != 1)
    {
        perror("EVP_DigestInit_ex failed");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    // First, hash the filename
    if (EVP_DigestUpdate(mdctx, filename, strlen(filename)) != 1)
    {
        perror("EVP_DigestUpdate failed on filename");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    FILE *file = fopen(filename, "rb");
    if (!file)
    {
        perror("Failed to open file");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

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

    // Finalize the digest and get the hash
    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1)
    {
        perror("EVP_DigestFinal_ex failed");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    // Convert hash to hex string
    for (unsigned int i = 0; i < hash_len; i++)
    {
        sprintf(output + (i * 2), "%02x", hash[i]);
    }
    output[hash_len * 2] = '\0';

    EVP_MD_CTX_free(mdctx);
}
*/

// Function to compute SHA-1 hash based on filename + content
void compute_sha1(const char *filename, char *output)
{
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    unsigned char buffer[BUFFER_SIZE];
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (!mdctx)
    {
        perror("Failed to create EVP_MD_CTX");
        exit(EXIT_FAILURE);
    }

    // Initialize the digest context for SHA-1
    if (EVP_DigestInit_ex(mdctx, EVP_sha1(), NULL) != 1)
    {
        perror("EVP_DigestInit_ex failed");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    // First, hash the filename (as a string)
    if (EVP_DigestUpdate(mdctx, filename, strlen(filename)) != 1)
    {
        perror("EVP_DigestUpdate failed on filename");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    // Open the file to hash its contents
    FILE *file = fopen(filename, "rb");
    if (!file)
    {
        perror("Failed to open file");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, file)) > 0)
    {
        // Hash the file content
        if (EVP_DigestUpdate(mdctx, buffer, bytes_read) != 1)
        {
            perror("EVP_DigestUpdate failed on file content");
            fclose(file);
            EVP_MD_CTX_free(mdctx);
            exit(EXIT_FAILURE);
        }
    }
    fclose(file);

    // Finalize the digest and get the hash
    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1)
    {
        perror("EVP_DigestFinal_ex failed");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    // Convert hash to hex string
    for (unsigned int i = 0; i < hash_len; i++)
    {
        sprintf(output + (i * 2), "%02x", hash[i]);
    }
    output[hash_len * 2] = '\0';

    EVP_MD_CTX_free(mdctx);
}

// Function to save the file based on its hash
void save_file_based_on_hash(const char *filename, const char *hash)
{
    // Create the directory structure based on the first two characters of the hash
    char dir_name[3]; // First two characters of the hash
    snprintf(dir_name, sizeof(dir_name), "%c%c", hash[0], hash[1]);

    // Create the directory if it doesn't exist
    if (mkdir(dir_name, 0755) == -1 && errno != EEXIST)
    { // EEXIST for existing directory
        perror("Failed to create directory");
        exit(EXIT_FAILURE);
    }

    size_t file_path_size = strlen(dir_name) + strlen(hash) + 2; // 1 for '/' and 1 for '\0'
    char *file_path = malloc(file_path_size);
    if (!file_path)
    {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }
    snprintf(file_path, file_path_size, "%s/%s", dir_name, hash);

    ///////////////////////////
    // **CHANGES: Check if the file already exists**
    struct stat file_stat;
    if (stat(file_path, &file_stat) == 0)
    {
        printf("File already exists in the system: %s\n", file_path);
        free(file_path);
        return;
    }
    ///////////////////////////

    // Open the original file and the destination file
    FILE *source_file = fopen(filename, "rb");
    if (!source_file)
    {
        perror("Failed to open source file");
        free(file_path); //
        exit(EXIT_FAILURE);
    }

    ///////////////////////////
    char lock_file_path[file_path_size + 5]; // +5 for ".lock"
    snprintf(lock_file_path, sizeof(lock_file_path), "%s.lock", file_path);

    int lock_fd = open(lock_file_path, O_CREAT | O_EXCL, 0644);
    if (lock_fd == -1)
    {
        perror("Failed to create lock file");
        fclose(source_file);
        free(file_path);
        exit(EXIT_FAILURE);
    }
    ///////////////////////////

    FILE *dest_file = fopen(file_path, "wb");
    if (!dest_file)
    {
        perror("Failed to create destination file");
        fclose(source_file);
        close(lock_fd);
        unlink(lock_file_path); // Remove lock file
        free(file_path);
        exit(EXIT_FAILURE);
    }

    // Copy the content of the source file to the destination
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
            unlink(lock_file_path); // Remove lock file
            free(file_path);
            exit(EXIT_FAILURE);
        }
    }
    if (ferror(source_file))
    {
        perror("Error reading source file");
        fclose(source_file);
        fclose(dest_file);
        close(lock_fd);
        unlink(lock_file_path); // Remove lock file
        free(file_path);
        exit(EXIT_FAILURE);
    }

    fclose(source_file);
    fclose(dest_file);
    close(lock_fd);
    unlink(lock_file_path); // Remove the lock file
    printf("File saved as %s\n", file_path);
    free(file_path);
}

// Function to delete the saved file based on its hash
void delete_file_based_on_hash_by_name(const char *hash)
{
    // Create the directory path based on the first two characters of the hash
    char dir_name[3]; // First two characters of the hash
    snprintf(dir_name, sizeof(dir_name), "%c%c", hash[0], hash[1]);

    // Create the full file path using the directory and hash as the filename
    size_t file_path_size = strlen(dir_name) + strlen(hash) + 2; // 1 for '/' and 1 for '\0'
    char *file_path = malloc(file_path_size);
    if (!file_path)
    {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }
    snprintf(file_path, file_path_size, "%s/%s", dir_name, hash);

    int retFlag;
    remove_file_using_filePath(file_path, &retFlag);
    if (retFlag == 1)
        return;

    delete_directory_if_empty(dir_name, file_path);
}

// Function to delete the file and its directory based on the hash
void delete_file_based_on_hash(const char *hash)
{
    // Ensure the hash is valid
    if (strlen(hash) != HASH_SIZE)
    {
        fprintf(stderr, "Invalid hash length\n");
        return;
    }

    // Create the directory path based on the first two characters of the hash
    char dir_name[3]; // First two characters of the hash
    snprintf(dir_name, sizeof(dir_name), "%c%c", hash[0], hash[1]);

    // Create the full file path using the directory and hash as the filename
    size_t file_path_size = strlen(dir_name) + strlen(hash) + 2; // 1 for '/' and 1 for '\0'
    char *file_path = malloc(file_path_size);
    if (!file_path)
    {
        perror("Memory allocation failed");
        return; // Memory allocation failed, exit early
    }
    snprintf(file_path, file_path_size, "%s/%s", dir_name, hash);

    int retFlag;
    // Remove the file using the helper function
    remove_file_using_filePath(file_path, &retFlag);
    if (retFlag == 1) // File could not be deleted (doesn't exist)
    {
        free(file_path); // Don't forget to free memory
        return;
    }

    // Remove the directory if it's empty using the helper function
    delete_directory_if_empty(dir_name, file_path);
}

void remove_file_using_filePath(char *file_path, int *retFlag)
{
    *retFlag = 1;
    // Check if the file exists before attempting to delete it
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

// Function to delete the directory if it's empty
void delete_directory_if_empty(char dir_name[3], char *file_path)
{
    // Attempt to remove the directory if empty
    if (rmdir(dir_name) == 0)
    {
        printf("Directory %s is now empty and deleted.\n", dir_name);
    }
    else
    {
        perror("Error deleting directory");
    }
}

// Function to delete a file based on its filename
void delete_file_by_name(const char *filename)
{
    // Try to delete the file
    if (remove(filename) == 0)
    {
        printf("File %s deleted successfully.\n", filename);
        delete_directory_if_empty(filename, filename);
    }
    else
    {
        perror("Error deleting file");
    }
}

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        fprintf(stderr, "Usage: %s <file>\n", argv[0]);
        return EXIT_FAILURE;
    }

    char hash[HASH_SIZE + 1];
    compute_sha1(argv[1], hash); // Calculate hash based on filename + content
    printf("SHA-1 hash: %s\n", hash);

    //save_file_based_on_hash(argv[1], hash); // Save the file based on its hash
    //delete_file_based_on_hash(hash);        // Delete the file based on its hash
    delete_file_based_on_hash_by_name(hash); // Delete the file based on its hash
    //delete_file_by_name(argv[1]); // Delete the file based on its filename
    return EXIT_SUCCESS;
}
