from pathlib import Path

import yaml
from tests.common import *


def test_bin_inner_dependency(runtime_dir):
    bin_project_type = "bin"
    bin_name = "my_bin"
    new_project([bin_project_type, bin_name])

    # Create 'my_bin_2' inner dependency of 'my_bin'
    bin_2_name = "my_bin_2"
    new_inner_project(bin_name, ["-e", bin_project_type, bin_2_name])

    # Add 'my_bin_2' as dependency of 'my_bin'
    add_dependency(bin_name, [bin_2_name])

    # Create 'lib' inner dependency of 'my_bin'
    lib_project_type = "lib"
    lib_name = "my_lib"
    new_inner_project(bin_name, ["-e", lib_project_type, lib_name])

    # Add 'my_lib' as dependency of 'my_bin'
    add_dependency(bin_name, [lib_name])

    # Create 'dyn' inner dependency of 'my_bin'
    dyn_project_type = "dyn"
    dyn_name = "my_dyn"
    new_inner_project(bin_name, ["-e", dyn_project_type, dyn_name])

    # Add 'my_lib' as dependency of 'my_bin'
    add_dependency(bin_name, [dyn_name])



    # Load the yaml and validate values
    with open(RUNTIME_DIR / bin_name / "kiss.yaml" , "r") as f:
        data = yaml.safe_load(f)

        # assert bin
        bin_root = data[bin_project_type]
        assert len(bin_root) == 2
        bin_project = bin_root[0]
        assert "name" in bin_project
        assert bin_project["name"] == bin_name
        assert "version" in bin_project
        assert bin_project["version"] == "0.1.0"
        assert "sources" in bin_project
        assert len(bin_project["sources"]) == 1
        assert Path(bin_project["sources"][0]) == Path('src/main.cpp')
        assert "dependencies" in bin_project
        assert bin_project["dependencies"][0]["name"] == bin_2_name
        assert bin_project["dependencies"][1]["name"] == lib_name
        assert bin_project["dependencies"][2]["name"] == dyn_name
        assert "description" not in bin_project
        assert "path" not in bin_project
        bin_2_project = bin_root[1]
        assert "name" in bin_2_project
        assert bin_2_project["name"] == bin_2_name
        assert "version" in bin_2_project
        assert bin_2_project["version"] == "0.1.0"
        assert "sources" in bin_2_project
        assert len(bin_2_project["sources"]) == 1
        assert Path(bin_2_project["sources"][0]) == Path('src/main.cpp')
        assert "dependencies" not in bin_2_project
        assert "description" not in bin_2_project
        assert "path" in bin_2_project
        assert bin_2_project["path"] == bin_2_name

        # assert lib
        lib_root = data[lib_project_type]
        lib_project = lib_root[0]
        assert "name" in lib_project
        assert lib_project["name"] == lib_name
        assert "version" in lib_project
        assert lib_project["version"] == "0.1.0"
        assert "sources" in lib_project
        assert len(lib_project["sources"]) == 1
        assert Path(lib_project["sources"][0]) == Path('src/lib.cpp')
        assert "interface_directories" in lib_project
        assert len(lib_project["interface_directories"]) == 1
        assert lib_project["interface_directories"][0] == 'interface'
        assert "dependencies" not in lib_project
        assert "description" not in lib_project
        assert "path" in lib_project
        assert lib_project["path"] == lib_name


        # assert dyn
        dyn_root = data[dyn_project_type]
        dyn_project = dyn_root[0]
        assert "name" in dyn_project
        assert dyn_project["name"] == dyn_name
        assert "version" in dyn_project
        assert dyn_project["version"] == "0.1.0"
        assert "sources" in dyn_project
        assert len(dyn_project["sources"]) == 1
        assert Path(dyn_project["sources"][0]) == Path('src/dyn.cpp')
        assert "interface_directories" in dyn_project
        assert len(dyn_project["interface_directories"]) == 1
        assert dyn_project["interface_directories"][0] == 'interface'
        assert "dependencies" not in dyn_project
        assert "description" not in dyn_project
        assert "path" in dyn_project
        assert dyn_project["path"] == dyn_name


def test_lib_inner_dependency(runtime_dir):
    lib_project_type = "lib"
    lib_name = "my_lib"
    new_project([lib_project_type, lib_name])

    # Create 'my_lib_2' inner dependency of 'my_lib'
    lib_2_name = "my_lib_2"
    new_inner_project(lib_name, ["-e", lib_project_type, lib_2_name])

    # Add 'my_lib_2' as dependency of 'my_lib'
    add_dependency(lib_name, [lib_2_name])

    # Create 'bin' inner dependency of 'my_lib'
    bin_project_type = "bin"
    bin_name = "my_bin"
    new_inner_project(lib_name, ["-e", bin_project_type, bin_name])

    # Add 'my_bin' as dependency of 'my_lib'
    add_dependency(lib_name, [bin_name])

    # Create 'dyn' inner dependency of 'my_lib'
    dyn_project_type = "dyn"
    dyn_name = "my_dyn"
    new_inner_project(lib_name, ["-e", dyn_project_type, dyn_name])

    # Add 'my_dyn' as dependency of 'my_lib'
    add_dependency(lib_name, [dyn_name])



    # Load the yaml and validate values
    with open(RUNTIME_DIR / lib_name / "kiss.yaml" , "r") as f:
        data = yaml.safe_load(f)

        # assert bin
        lib_root = data[lib_project_type]
        assert len(lib_root) == 2
        lib_project = lib_root[0]
        assert "name" in lib_project
        assert lib_project["name"] == lib_name
        assert "version" in lib_project
        assert lib_project["version"] == "0.1.0"
        assert "sources" in lib_project
        assert len(lib_project["sources"]) == 1
        assert Path(lib_project["sources"][0]) == Path('src/lib.cpp')
        assert "interface_directories" in lib_project
        assert len(lib_project["interface_directories"]) == 1
        assert lib_project["interface_directories"][0] == 'interface'
        assert "dependencies" in lib_project
        assert lib_project["dependencies"][0]["name"] == lib_2_name
        assert lib_project["dependencies"][1]["name"] == bin_name
        assert lib_project["dependencies"][2]["name"] == dyn_name
        assert "description" not in lib_project
        assert "path" not in lib_project
        lib_2_project = lib_root[1]
        assert "name" in lib_2_project
        assert lib_2_project["name"] == lib_2_name
        assert "version" in lib_2_project
        assert lib_2_project["version"] == "0.1.0"
        assert "sources" in lib_2_project
        assert len(lib_2_project["sources"]) == 1
        assert Path(lib_2_project["sources"][0]) == Path('src/lib.cpp')
        assert "interface_directories" in lib_2_project
        assert len(lib_2_project["interface_directories"]) == 1
        assert lib_2_project["interface_directories"][0] == 'interface'
        assert "dependencies" not in lib_2_project
        assert "description" not in lib_2_project
        assert "path" in lib_2_project
        assert lib_2_project["path"] == lib_2_name

        # assert bin
        bin_root = data[bin_project_type]
        bin_project = bin_root[0]
        assert "name" in bin_project
        assert bin_project["name"] == bin_name
        assert "version" in bin_project
        assert bin_project["version"] == "0.1.0"
        assert "sources" in bin_project
        assert len(bin_project["sources"]) == 1
        assert Path(bin_project["sources"][0]) == Path('src/main.cpp')
        assert "dependencies" not in bin_project
        assert "description" not in bin_project
        assert "path" in bin_project
        assert bin_project["path"] == bin_name


        # assert dyn
        dyn_root = data[dyn_project_type]
        dyn_project = dyn_root[0]
        assert "name" in dyn_project
        assert dyn_project["name"] == dyn_name
        assert "version" in dyn_project
        assert dyn_project["version"] == "0.1.0"
        assert "sources" in dyn_project
        assert len(dyn_project["sources"]) == 1
        assert Path(dyn_project["sources"][0]) == Path('src/dyn.cpp')
        assert "interface_directories" in dyn_project
        assert len(dyn_project["interface_directories"]) == 1
        assert dyn_project["interface_directories"][0] == 'interface'
        assert "dependencies" not in dyn_project
        assert "description" not in dyn_project
        assert "path" in dyn_project
        assert dyn_project["path"] == dyn_name


def test_dyn_inner_dependency(runtime_dir):
    dyn_project_type = "dyn"
    dyn_name = "my_dyn"
    new_project([dyn_project_type, dyn_name])

    # Create 'my_lib_2' inner dependency of 'my_dyn'
    dyn_2_name = "my_dyn_2"
    new_inner_project(dyn_name, ["-e", dyn_project_type, dyn_2_name])

    # Add 'my_bin_2' as dependency of 'my_dyn'
    add_dependency(dyn_name, [dyn_2_name])

    # Create 'bin' inner dependency of 'my_dyn'
    bin_project_type = "bin"
    bin_name = "my_bin"
    new_inner_project(dyn_name, ["-e", bin_project_type, bin_name])

    # Add 'my_bin' as dependency of 'my_dyn'
    add_dependency(dyn_name, [bin_name])

    # Create 'dyn' inner dependency of 'my_dyn'
    lib_project_type = "lib"
    lib_name = "my_lib"
    new_inner_project(dyn_name, ["-e", lib_project_type, lib_name])

    # Add 'my_lib' as dependency of 'my_dyn'
    add_dependency(dyn_name, [lib_name])



    # Load the yaml and validate values
    with open(RUNTIME_DIR / dyn_name / "kiss.yaml" , "r") as f:
        data = yaml.safe_load(f)

        # assert bin
        dyn_root = data[dyn_project_type]
        assert len(dyn_root) == 2
        dyn_project = dyn_root[0]
        assert "name" in dyn_project
        assert dyn_project["name"] == dyn_name
        assert "version" in dyn_project
        assert dyn_project["version"] == "0.1.0"
        assert "sources" in dyn_project
        assert len(dyn_project["sources"]) == 1
        assert Path(dyn_project["sources"][0]) == Path('src/dyn.cpp')
        assert "interface_directories" in dyn_project
        assert len(dyn_project["interface_directories"]) == 1
        assert dyn_project["interface_directories"][0] == 'interface'
        assert "dependencies" in dyn_project
        assert dyn_project["dependencies"][0]["name"] == dyn_2_name
        assert dyn_project["dependencies"][1]["name"] == bin_name
        assert dyn_project["dependencies"][2]["name"] == lib_name
        assert "description" not in dyn_project
        assert "path" not in dyn_project
        dyn_2_project = dyn_root[1]
        assert "name" in dyn_2_project
        assert dyn_2_project["name"] == dyn_2_name
        assert "version" in dyn_2_project
        assert dyn_2_project["version"] == "0.1.0"
        assert "sources" in dyn_2_project
        assert len(dyn_2_project["sources"]) == 1
        assert Path(dyn_2_project["sources"][0]) == Path('src/dyn.cpp')
        assert "interface_directories" in dyn_2_project
        assert len(dyn_2_project["interface_directories"]) == 1
        assert dyn_2_project["interface_directories"][0] == 'interface'
        assert "dependencies" not in dyn_2_project
        assert "description" not in dyn_2_project
        assert "path" in dyn_2_project
        assert dyn_2_project["path"] == dyn_2_name

        # assert bin
        bin_root = data[bin_project_type]
        bin_project = bin_root[0]
        assert "name" in bin_project
        assert bin_project["name"] == bin_name
        assert "version" in bin_project
        assert bin_project["version"] == "0.1.0"
        assert "sources" in bin_project
        assert len(bin_project["sources"]) == 1
        assert Path(bin_project["sources"][0]) == Path('src/main.cpp')
        assert "dependencies" not in bin_project
        assert "description" not in bin_project
        assert "path" in bin_project
        assert bin_project["path"] == bin_name


        # assert lib
        lib_root = data[lib_project_type]
        lib_project = lib_root[0]
        assert "name" in lib_project
        assert lib_project["name"] == lib_name
        assert "version" in lib_project
        assert lib_project["version"] == "0.1.0"
        assert "sources" in lib_project
        assert len(lib_project["sources"]) == 1
        assert Path(lib_project["sources"][0]) == Path('src/lib.cpp')
        assert "interface_directories" in lib_project
        assert len(lib_project["interface_directories"]) == 1
        assert lib_project["interface_directories"][0] == 'interface'
        assert "dependencies" not in lib_project
        assert "description" not in lib_project
        assert "path" in lib_project
        assert lib_project["path"] == lib_name


def test_git_dependency(runtime_dir):
    bin_project_type = "bin"
    bin_name = "my_bin"
    new_project([bin_project_type, bin_name])

    # Create 'gtest' inner dependency of 'my_bin'
    gtest_name = "gtest"
    gtest_address = "git@github.com:google/googletest.git"
    add_dependency(bin_name, [gtest_name, "--git", gtest_address])


    # Load the yaml and validate values
    with open(RUNTIME_DIR / bin_name / "kiss.yaml" , "r") as f:
        data = yaml.safe_load(f)

        # assert bin
        bin_root = data[bin_project_type]
        assert len(bin_root) == 1
        bin_project = bin_root[0]
        assert "name" in bin_project
        assert bin_project["name"] == bin_name
        assert "version" in bin_project
        assert bin_project["version"] == "0.1.0"
        assert "sources" in bin_project
        assert len(bin_project["sources"]) == 1
        assert Path(bin_project["sources"][0]) == Path('src/main.cpp')
        assert "dependencies" in bin_project
        assert bin_project["dependencies"][0]["name"] == gtest_name
        assert bin_project["dependencies"][0]["git"] == gtest_address
        assert "description" not in bin_project
        assert "path" not in bin_project

