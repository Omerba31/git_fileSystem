#ifndef BLOB_H
#define BLOB_H

#include <string>

class Blob{
  public:
    const std::string hash;

    // Constructor for lvalue reference
    Blob(const std::string& hash) : hash(hash) {}

    // Constructor for rvalue reference
    Blob(std::string&& hash) : hash(std::move(hash)) {}

};

#endif //BLOB_H
