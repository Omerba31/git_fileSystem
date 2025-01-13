#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "caf.h"
#include "hashTypes.h" 
#include "object_io.h" 

using namespace std;
namespace py = pybind11;

template<typename R, typename... Args>
auto make_exception_handler(R (*f)(Args...)) {
    return [f](Args... args) -> R {
        try {
            return f(std::forward<Args>(args)...);
        } catch (const std::exception& e) {
            throw py::value_error(e.what());
        }
    };
}

// Specialization for void return type
template<typename... Args>
auto make_exception_handler(void (*f)(Args...)) {
    return [f](Args... args) {
        try {
            f(std::forward<Args>(args)...);
        } catch (const std::exception& e) {
            throw py::value_error(e.what());
        }
    };
}

PYBIND11_MODULE(_libcaf, m) {

//methods

    // caf
    m.def("hash_file", make_exception_handler(hash_file));
    m.def("hash_string", make_exception_handler(hash_string));
    m.def("save_file_content", make_exception_handler(save_file_content));
    m.def("open_fd_for_saving_content", make_exception_handler(open_fd_for_saving_content));
    m.def("delete_content", make_exception_handler(delete_content));
    m.def("open_fd_for_reading_content", make_exception_handler(open_fd_for_reading_content));
    m.def("close_content_fd", make_exception_handler(close_content_fd));

    // hashTypes
    m.def("hash_object", py::overload_cast<const Blob&>(&hash_object), py::arg("blob"));
    m.def("hash_object", py::overload_cast<const Tree&>(&hash_object), py::arg("tree"));
    m.def("hash_object", py::overload_cast<const Commit&>(&hash_object), py::arg("commit"));

    // object_io
    m.def("save_commit", &save_commit);
    m.def("load_commit", &load_commit);
    m.def("save_tree", &save_tree);
    m.def("load_tree", &load_tree);

//classes

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
    .def_readonly("name", &TreeRecord::name)
    .def("__eq__", [](const TreeRecord &self, const TreeRecord &other) {
        return self.type == other.type && self.hash == other.hash && self.name == other.name;
    });

    py::class_<Tree>(m, "Tree")
    .def(py::init<const std::map<std::string, TreeRecord>&>())
    .def("get_records", &Tree::getRecords);

    py::class_<Commit>(m, "Commit")
        .def(py::init<const string &, const string&, const string&, time_t, const std::optional<std::string>&>())
        .def_readonly("treeHash", &Commit::treeHash)
        .def_readonly("author", &Commit::author)
        .def_readonly("message", &Commit::message)
        .def_readonly("timestamp", &Commit::timestamp)
        .def_readonly("parent", &Commit::parent);
}