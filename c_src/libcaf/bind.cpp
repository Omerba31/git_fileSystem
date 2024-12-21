#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "caf.h"
#include "hashTypes.h" //containes everything needed

using namespace std;
namespace py = pybind11;

PYBIND11_MODULE(_libcaf, m) {

//methods

    // caf
    m.def("compute_hash", [](const std::string& filename) -> std::pair<int, std::string> {
        char hash[HASH_SIZE + 1]; // Buffer to store the hash
        int result = compute_hash(filename.c_str(), hash);
        return std::make_pair(result, std::string(hash));
    }, py::arg("filename"));

    m.def("open_content", &open_content);
    m.def("save_content", &save_content);
    m.def("delete_content", &delete_content);

    //hashTypes
    m.def("computeHash", py::overload_cast<const Blob&>(&computeHash), py::arg("blob"));
    m.def("computeHash", py::overload_cast<const Tree&>(&computeHash), py::arg("tree"));
    m.def("computeHash", py::overload_cast<const Commit&>(&computeHash), py::arg("commit"));


//classess

    py::class_<Blob>(m, "Blob")
    .def(py::init<std::string>())
    .def_readonly("hash", &Blob::hash);

    py::enum_<TreeRecord::Type>(m, "TreeRecordType")
    .value("TREE", TreeRecord::Type::TREE)
    .value("BLOB", TreeRecord::Type::BLOB)
    .value("COMMIT", TreeRecord::Type::COMMIT)
    .export_values();

    py::class_<TreeRecord>(m, "TreeRecord")
    .def(py::init<TreeRecord::Type, std::string, std::string>())
    .def_readonly("type", &TreeRecord::type)
    .def_readonly("hash", &TreeRecord::hash)
    .def_readonly("name", &TreeRecord::name);

    py::class_<Tree>(m, "Tree")
    .def(py::init<const std::map<std::string, TreeRecord>&>())
    .def("get_records", &Tree::getRecords);

    py::class_<Commit>(m, "Commit")
        .def(py::init<const string &, const string&, const string&, time_t>())
        .def_readonly("treeHash", &Commit::treeHash)
        .def_readonly("author", &Commit::author)
        .def_readonly("message", &Commit::message)
        .def_readonly("timestamp", &Commit::timestamp);
}