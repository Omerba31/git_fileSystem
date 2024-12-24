import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import find_packages, setup

setup(name='libcaf',
      ext_modules=[Pybind11Extension('_libcaf',
                                     ['src/caf.cpp',
                                      'src/hashTypes.cpp',
                                      'src/object_io.cpp',
                                      'src/bind.cpp'],
                                     include_dirs=[pybind11.get_include()],
                                     language='c++',
                                     extra_compile_args=['-O3', '-Wall', '-Werror', '-std=c++17'],
                                     extra_link_args=['-lcrypto'])],
      packages=find_packages(),
      package_dir={"": "."},
      cmdclass={"build_ext": build_ext})
