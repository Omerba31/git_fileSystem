import os

def open_file_by_hash(filename):
    # Dummy implementation for demonstration purposes
    # In a real scenario, this function would compute the hash and open the file accordingly
    try:
        fd = os.open(filename, os.O_RDONLY)
    except OSError as e:
        print(f"Error: {e}")
        fd = -1

    # Check if the file descriptor is valid
    if fd == -1:
        print(f"Error: Could not open file for {filename}")
    else:
        print(f"File opened successfully with file descriptor: {fd}")
    
    return fd
