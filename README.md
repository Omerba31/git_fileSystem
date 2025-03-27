# Git FileSystem

A hybrid Git-like file system project that combines the performance of C++ with the flexibility of a Python command-line interface. It mimics essential Git operations such as creating objects, managing trees, and committing changes — all within a custom file system environment.

---

## 🧠 Project Structure

- **C++ Core (`libcaf/src/`)**: Implements the core logic for managing blobs, trees, commits, object I/O, and hashing.
- **Python CLI (`caf/`)**: Provides a user-friendly interface for interacting with the file system via commands.
- **Binding Layer**: Exposes C++ functionality to Python (via bindings in `bind.cpp` and setup config).

---

## 🚀 Features

- Create and manage Git-like objects (blobs, trees, commits)
- Navigate a custom file system hierarchy
- Interact through Python-based CLI
- Modular, extensible, and performance-focused

---

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- A C++ compiler (`g++` or `clang`)
- `pip` and `virtualenv` (optional but recommended)

### Clone the repository

```bash
git clone https://github.com/Omerba31/git_fileSystem.git
cd git_fileSystem
```

### Build and install the C++ extension

```bash
cd libcaf
pip install .
```

> This will compile the C++ source in `libcaf/src/` and make it available to the Python interface.

### Run the CLI

```bash
cd ../caf
python -m caf
```

---

## 🧪 Running Tests

```bash
cd tests
pytest
```

---

## 📁 Directory Overview

```
git_fileSystem/
├── caf/             # Python CLI interface
├── libcaf/          # C++ backend and binding setup
│   ├── src/         # Core C++ logic (Blob, Tree, Commit, etc.)
│   └── setup.py     # Build configuration for Python bindings
├── tests/           # Unit tests
├── Makefile         # Optional build automation
└── Dockerfile       # Containerization setup
```

---

## 🧩 Example Commands

From the CLI:

```bash
> init
Initialized empty Git-like repository.

> add file.txt
Staged 'file.txt'

> commit -m "Initial commit"
[commit] Created with message: Initial commit

> ls
.blob
.tree
```

---

## 📄 License

This project is licensed under the **MIT License**. See `LICENSE` for details.

---

## 🤝 Contributions

Feel free to open issues, suggest features, or submit pull requests!
