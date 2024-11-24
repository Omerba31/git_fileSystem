#ifndef FILE_UTILS_H
#define FILE_UTILS_H

#include <stdio.h>
#include <stdlib.h>

#define HASH_SIZE 40     // SHA-1 hash size (in characters)
#define BUFFER_SIZE 4096 // Buffer size for file operations
#define DIR_NAME_SIZE 2  // Number of characters from hash used for directory name


// Macro for safe index advancement
#define PATH_ADVANCE(index) do { \
    if ((index) >= PATH_MAX) { \
        return -1; \
    } \
    (index)++; \
} while (0)

/**
 * @brief Deletes a file based on its hash value.
 *
 * @param hash The hash value of the file to delete.
 */
int delete_file_based_on_hash(const char *root_dir, const char *hash);

/**
 * @brief Opens a file based on its root directory and hash.
 *
 * @param root_dir The root directory containing the file.
 * @param hash The hash value of the file.
 * @return A file descriptor or an error code.
 */
int open_content(const char *root_dir, const char *hash);

/**
 * @brief Saves a file with a given name and hash.
 *
 * @param filename The name of the file to save.
 * @param hash The hash value associated with the file.
 */
int save_file(const char *filename, const char *hash);

/**
 * @brief Computes the SHA-1 hash of a file.
 *
 * @param filename The name of the file to compute the hash for.
 * @param output A buffer to store the computed hash value (should be at least 41 bytes long).
 */
int compute_sha1(const char *filename, char *output);

/**
 * @brief Copies the contents of one file to another.
 *
 * @param src The source file path.
 * @param dest The destination file path.
 * @return 0 on success, or an error code on failure.
 */
int copy_file(const char *src, const char *dest);

/**
 * @brief Removes a specified file.
 *
 * @param file_path The path of the file to remove.
 * @return 0 on success, or an error code on failure.
 */
int remove_file(const char *file_path);

/**
 * @brief Deletes an empty directory.
 *
 * @param dir_name The name of the directory to delete.
 */
int delete_empty_directory(const char *dir_name);

#endif // FILE_UTILS_H
