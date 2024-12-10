#ifndef TREERECORD_H
#define TREERECORD_H

#include <string>

class TreeRecord {
public:

    // Enum for type of tree node
    enum class Type {
        TREE,
        BLOB,
        COMMIT
    };
    
    const Type type;         // tree or blob or commit
    const int hash;          // unique identifier for the object
    const std::string name;  // name of the record

    // Constructor
    TreeRecord(Type type, int hash, std::string name) 
        : type(type), hash(hash), name(std::move(name)) {}
};

#endif // TREERECORD_H
