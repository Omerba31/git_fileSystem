#include <pybind11/pybind11.h>

#include "caf.h"
#include "commit.h"

using namespace std;
namespace py = pybind11;

PYBIND11_MODULE(_libcaf, m) {
    m.def("compute_sha1",  [](std::string filename) ->pair<int, string> {
        string buffer(HASH_SIZE + 1, '\0');  // Create a string with a null-terminated buffer
        int result = compute_sha1(filename.c_str(), buffer.data());
        return pair(result, string(buffer.c_str()));
        }, py::arg("filename"));
    m.def("open_content", &open_content);
    m.def("save_content", &save_content);
    m.def("delete_content", &delete_content);

    py::class_<Commit>(m, "Commit")
        .def(py::init<const string &, const string&, const string&, time_t>())
        .def_readonly("treeHash", &Commit::treeHash)
        .def_readonly("author", &Commit::author)
        .def_readonly("message", &Commit::message)
        .def_readonly("timestamp", &Commit::timestamp);
}