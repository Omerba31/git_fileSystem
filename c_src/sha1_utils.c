#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include "sha1_utils.h"

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
    if (EVP_DigestInit_ex(mdctx, EVP_sha1(), NULL) != 1)
    {
        perror("EVP_DigestInit_ex failed");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

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

    if (EVP_DigestFinal_ex(mdctx, hash, &hash_len) != 1)
    {
        perror("EVP_DigestFinal_ex failed");
        EVP_MD_CTX_free(mdctx);
        exit(EXIT_FAILURE);
    }

    for (unsigned int i = 0; i < hash_len; i++)
    {
        sprintf(output + (i * 2), "%02x", hash[i]);
    }
    output[hash_len * 2] = '\0';
    EVP_MD_CTX_free(mdctx);
}
