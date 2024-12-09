import ctypes
import os

class FileManager:
    def __init__(self, lib_path):
        self.lib = ctypes.CDLL(lib_path)

        # Define the argument and return types for the C functions
        self.lib.open_content.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.open_content.restype = ctypes.c_int

        self.lib.compute_sha1.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.compute_sha1.restype = ctypes.c_int

        self.lib.save_content.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.save_content.restype = None

        self.lib.delete_content.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.delete_content.restype = None

    def compute_sha1(self, filename):
        hash_output = ctypes.create_string_buffer(41)
        result = self.lib.compute_sha1(filename.encode('utf-8'), hash_output)
        if result == -1:
            raise FileNotFoundError(f"File '{filename}' not found.")
        if result != 0:
            errno = ctypes.get_errno()
            error_message = f"Failed to compute SHA1 for file '{filename}'. Error code: {errno}, Description: {os.strerror(errno)}"
            raise OSError(errno, error_message)
        return hash_output.value.decode('utf-8')

    def save_content(self, root_dir, filename):
        self.lib.save_content(root_dir.encode('utf-8'), filename.encode('utf-8'))

    def open_content(self, root_dir, hash_value):
        result = self.lib.open_content(root_dir.encode('utf-8'), hash_value.encode('utf-8'))
        if result == -1:
            raise OSError(f"Failed to open content with hash '{hash_value}' in directory '{root_dir}'")
        return result

    def delete_content(self, root_dir, hash_value):
        self.lib.delete_content(root_dir.encode('utf-8'), hash_value.encode('utf-8'))


    def create_test_file(self, dir_path, filename, content):
        full_path = os.path.join(dir_path, filename)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as file:
            file.write(content)
        return full_path
