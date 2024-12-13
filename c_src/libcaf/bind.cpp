#include <pybind11/pybind11.h>

#include "caf.h"
#include "hashTypes.h" //containes everything needed

using namespace std;
namespace py = pybind11;

PYBIND11_MODULE(_libcaf, m) {

//methods

    //caf
    m.def("compute_sha1", [](std::string filename) -> std::pair<int, std::string> {
        std::string hash;
        int result = compute_sha1(filename, hash);
        return std::make_pair(result, hash);
    }, py::arg("filename"));

    m.def("open_content", &open_content);
    m.def("save_content", &save_content);
    m.def("delete_content", &delete_content);

    //hashTypes
    m.def("computeHash_blob", py::overload_cast<const Blob&>(&computeHash), py::arg("blob"));
    m.def("computeHash_treeRecord", py::overload_cast<const TreeRecord&>(&computeHash), py::arg("treeRecord"));
    m.def("computeHash_tree", py::overload_cast<const Tree&>(&computeHash), py::arg("tree"));
    m.def("computeHash_commit", py::overload_cast<const Commit&>(&computeHash), py::arg("commit"));


//classess

    //Blob
    py::class_<Blob>(m, "Blob")
    .def(py::init<std::string>())
    .def_readonly("hash", &Blob::hash);

    //TreeRecord
    py::class_<TreeRecord>(m, "TreeRecord")
    .def(py::init<TreeRecord::Type, std::string, std::string>())
    .def_readonly("type", &TreeRecord::type)
    .def_readonly("hash", &TreeRecord::hash)
    .def_readonly("name", &TreeRecord::name);

    //Tree
    py::class_<Tree>(m, "Tree")
    .def(py::init<const std::map<std::string, TreeRecord>&>())
    .def("get_records", &Tree::getRecords);

    //Commit
    py::class_<Commit>(m, "Commit")
        .def(py::init<const string &, const string&, const string&, time_t>())
        .def_readonly("treeHash", &Commit::treeHash)
        .def_readonly("author", &Commit::author)
        .def_readonly("message", &Commit::message)
        .def_readonly("timestamp", &Commit::timestamp);
}