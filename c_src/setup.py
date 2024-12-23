import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

setup(name='libcaf',
      ext_modules=[Pybind11Extension('_libcaf',
                                     ['libcaf/caf.cpp',
                                      'libcaf/hashTypes.cpp',
                                      'libcaf/object_io.cpp',
                                      'libcaf/bind.cpp'],
                                     include_dirs=[pybind11.get_include()],
                                     language='c++',
                                     extra_compile_args=['-O3', '-Wall', '-Werror',  '-std=c++17'],
                                     extra_link_args=['-lcrypto'])],
      packages=['libcaf'],
      cmdclass={"build_ext": build_ext})
