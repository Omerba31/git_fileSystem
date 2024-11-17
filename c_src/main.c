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

// Function to compute SHA-1 hash of a file using EVP API
void compute_sha1(const char *filename, char *output) {
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    unsigned char buffer[BUFFER_SIZE];
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (!mdctx) {
        perror("Failed to create EVP_MD_CTX");
        exit(EXIT_FAILURE);
    }

    FILE *file = fopen(filename, "rb");
    if (!file) {
        perror("Failed to open file");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    // Initialize the digest context for SHA-1
    if (EVP_DigestInit_ex(mdctx, EVP_sha1(), NULL) != 1) {
        perror("EVP_DigestInit_ex failed");
        fclose(file);
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, file)) > 0) {
        if (EVP_DigestUpdate(mdctx, buffer, bytes_read) != 1) {
            perror("EVP_DigestUpdate failed");
            fclose(file);
            EVP_MD_CTX_free(mdctx);
            exit(EXIT_FAILURE);
        }
    }
    fclose(file);

    // Finalize the digest and get the hash
    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1) {
        perror("EVP_DigestFinal_ex failed");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    // Convert hash to hex string
    for (unsigned int i = 0; i < hash_len; i++) {
        sprintf(output + (i * 2), "%02x", hash[i]);
    }
    output[hash_len * 2] = '\0';

    EVP_MD_CTX_free(mdctx);
}

// Function to save the file based on its hash
void save_file_based_on_hash(const char *filename, const char *hash) {
    // Create the directory structure based on the first two characters of the hash
    char dir_name[3]; // First two characters of the hash
    snprintf(dir_name, sizeof(dir_name), "%c%c", hash[0], hash[1]);

    // Create the directory if it doesn't exist
    if (mkdir(dir_name, 0777) == -1 && errno != EEXIST) { // EEXIST for existing directory
        perror("Failed to create directory");
        exit(EXIT_FAILURE);
    }

    // Create the file path using the hash as the filename
    char file_path[256];
    snprintf(file_path, sizeof(file_path), "%s/%s", dir_name, hash);

    // Open the original file and the destination file
    FILE *source_file = fopen(filename, "rb");
    if (!source_file) {
        perror("Failed to open source file");
        exit(EXIT_FAILURE);
    }

    FILE *dest_file = fopen(file_path, "wb");
    if (!dest_file) {
        perror("Failed to create destination file");
        fclose(source_file);
        exit(EXIT_FAILURE);
    }

    // Copy the content of the source file to the destination
    unsigned char buffer[BUFFER_SIZE];
    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, source_file)) > 0) {
        fwrite(buffer, 1, bytes_read, dest_file);
    }

    fclose(source_file);
    fclose(dest_file);
}

// Main function to test the compute_sha1 and save_file_based_on_hash functions
int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <file>\n", argv[0]);
        return EXIT_FAILURE;
    }

    char hash[HASH_SIZE + 1];
    compute_sha1(argv[1], hash);

    printf("SHA-1: %s\n", hash);

    // Save the file based on its SHA-1 hash
    save_file_based_on_hash(argv[1], hash);

    return EXIT_SUCCESS;
}
