#include "tree.h"

// Constructor
Tree::Tree(Type type, int hash, std::string name) 
    : type(type), hash(hash), name(std::move(name)) {}

// Getters
Type Tree::getType() const {
    return type;
}

int Tree::getHash() const {
    return hash;
}

std::string Tree::getName() const {
    return name;
}
