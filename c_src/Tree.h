#ifndef TREE_H
#define TREE_H

#include <string>

// Enum for type of tree node
enum class Type {
    TREE,
    BLOB,
    COMMIT
};

class Tree {
private:
    const Type type;    // tree or blob                             
    const int hash; 
    const std::string name; 

public:
    // Constructor
    Tree(Type type, int hash, std::string name);

    // Getters
    Type getType() const;
    int getHash() const;
    std::string getName() const;
};

#endif // TREE_H
