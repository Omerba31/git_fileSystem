import ctypes
import os

class FileManager:
    def __init__(self, lib_path):
        self.lib = ctypes.CDLL(lib_path)

        # Define the argument and return types for the C functions
        self.lib.open_content.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.open_content.restype = ctypes.c_int

        self.lib.compute_sha1.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.compute_sha1.restype = None

        self.lib.save_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.save_file.restype = None

    def compute_sha1(self, filename):
        hash_output = ctypes.create_string_buffer(41)  # SHA1 hash is 40 characters + null terminator
        self.lib.compute_sha1(filename.encode('utf-8'), hash_output)
        return hash_output.value.decode('utf-8')

    def save_file(self, root_dir, filename):
        self.lib.save_file(root_dir.encode('utf-8'), filename.encode('utf-8'))

    def open_content(self, root_dir, hash_value):
        return self.lib.open_content(root_dir.encode('utf-8'), hash_value.encode('utf-8'))