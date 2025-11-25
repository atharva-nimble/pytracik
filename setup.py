"""
Setup script for pytracik - TracIK Python Bindings

This wraps the platform-specific setup logic for use with pip/uv.
"""

import fnmatch
import os
import platform
import sys
import sysconfig

import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup


# Get the directory where setup.py is located
HERE = os.path.abspath(os.path.dirname(__file__))


def find_files(path, file_extension, visited=None, finded_files=None):
    if finded_files is None:
        finded_files = []
    if visited is None:
        visited = set()

    path_real = os.path.realpath(path)
    if path_real in visited:
        return finded_files
    visited.add(path_real)

    if os.path.isfile(path):
        if fnmatch.fnmatch(path, "*" + file_extension):
            # Return path relative to setup.py directory
            rel_path = os.path.relpath(path, HERE)
            finded_files.append(rel_path)
        return finded_files

    if os.path.isdir(path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.exists(item_path):
                find_files(item_path, file_extension, visited, finded_files)
            else:
                print(f"Warning: Path {item_path} does not exist or is a broken symbolic link", file=sys.stderr)
    return finded_files


def requirements_from_file(file_name):
    file_path = os.path.join(HERE, file_name)
    if os.path.exists(file_path):
        return open(file_path).read().splitlines()
    return []


# Load version from file
version_file = os.path.join(HERE, "trac_ik/version.py")
with open(version_file, "r") as f:
    version = eval(f.read().strip().split("=")[-1])

module_name = "pytracik"
src_dir = os.path.join(HERE, "src")

# Get all src files (relative paths)
src_files = find_files(src_dir, ".cpp")

# Retrieve Python configuration
python_include = sysconfig.get_paths()["include"]
python_library = sysconfig.get_config_var("LDLIBRARY")
python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"

if python_library:
    python_lib = os.path.splitext(os.path.basename(python_library))[0].replace("lib", "")
else:
    python_lib = python_version

if platform.system() == "Linux":
    ext_modules = [
        Pybind11Extension(
            module_name,
            src_files,
            include_dirs=[
                pybind11.get_include(),
                python_include,
                "/usr/include/eigen3",
                "/usr/include/orocos/kdl",
                "/usr/include/",
                "/usr/include/boost",
            ],
            libraries=[
                "nlopt",
                "orocos-kdl",
                "boost_date_time",
                "boost_system",
                "boost_thread",
                python_lib,
            ],
            library_dirs=[
                "/usr/lib/x86_64-linux-gnu",
            ],
            language="c++",
            extra_compile_args=["-std=c++17"],
        ),
    ]
elif platform.system() == "Windows":
    # Windows configuration from setup_windows.py
    ext_modules = [
        Pybind11Extension(
            module_name,
            src_files,
            include_dirs=[
                pybind11.get_include(),
                python_include,
            ],
            language="c++",
            extra_compile_args=["/std:c++17"],
        ),
    ]
else:
    sys.exit(f"Unsupported platform: {platform.system()}")

setup(
    name="pytracik",
    version=version,
    description="TracIK Python Bindings",
    author="Hao Chen",
    author_email="chen960216@gmail.com",
    license="MIT",
    url="https://github.com/chenhaox/pytracik",
    keywords="robotics inverse kinematics",
    packages=["trac_ik"],
    include_package_data=True,
    platforms=["Linux", "Windows"],
    cmdclass={"build_ext": build_ext},
    ext_modules=ext_modules,
    install_requires=requirements_from_file("requirements.txt"),
    python_requires=">=3.9",
)
