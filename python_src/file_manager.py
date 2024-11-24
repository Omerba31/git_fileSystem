import ctypes
import os

class FileManager:
    def __init__(self, lib_path):
        self.lib = ctypes.CDLL(lib_path)

        # Define the argument and return types for the C functions
        self.lib.open_content.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.open_content.restype = ctypes.c_int

        self.lib.compute_sha1.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.compute_sha1.restype = ctypes.c_int  # Updated from None to int (➕)

        self.lib.save_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.save_file.restype = None

        self.lib.delete_file_based_on_hash.argtypes = [ctypes.c_char_p]
        self.lib.delete_file_based_on_hash.restype = None


    def compute_sha1(self, filename):
        hash_output = ctypes.create_string_buffer(41)  # SHA1 hash is 40 characters + null terminator
        result = self.lib.compute_sha1(filename.encode('utf-8'), hash_output)  # Get return value (➕)
        if result != 0:  # Check for non-zero return code indicating failure (➕)
            return ""  # Return an empty string for errors (➕)
        return hash_output.value.decode('utf-8')  # Return the hash on success (➕)

    def save_file(self, root_dir, filename):
        self.lib.save_file(root_dir.encode('utf-8'), filename.encode('utf-8'))

    def open_content(self, root_dir, hash_value):
        return self.lib.open_content(root_dir.encode('utf-8'), hash_value.encode('utf-8'))
    
    def delete_file_based_on_hash(self, root_dir, hash_value):
        self.lib.delete_file_based_on_hash(root_dir.encode('utf-8'), hash_value.encode('utf-8'))