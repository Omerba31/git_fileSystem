#ifndef TREE_H
#define TREE_H

#include <map>
#include <string>
#include <utility> // for std::move
#include "treeRecord.h"

class Tree {
public:
    // Custom comparator for TreeRecord::name
    struct NameComparator {
        bool operator()(const std::string& lhs, const std::string& rhs) const {
            return lhs < rhs; // Sort strings alphabetically
        }
    };

    const std::map<std::string, TreeRecord> records; 

    explicit Tree(const std::map<std::string, TreeRecord>& records): records(records) {}

    const std::map<std::string, TreeRecord>& getRecords() const {
        return records;
    }

    std::map<std::string, TreeRecord>::const_iterator getRecord(const std::string& key) const {
        return records.find(key);
    }
};

#endif // TREE_H
