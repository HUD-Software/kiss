from pathlib import Path

import yaml
from tests.runtime_fixture import runtime_dir, RUNTIME_DIR
from tests.common import new_project

def test_new_lib_default(runtime_dir):
    project_type = "lib"
    project_name = "my_lib"
    new_project([project_type, project_name])

    # Load the yaml and validate values
    with open(RUNTIME_DIR / project_name / "kiss.yaml" , "r") as f:
        data = yaml.safe_load(f)
        bin_root = data[project_type]
        assert len(bin_root) == 1
        first_project = bin_root[0]
        assert "name" in first_project
        assert first_project["name"] == project_name
        assert "version" in first_project
        assert first_project["version"] == "0.1.0"
        assert "sources" in first_project
        assert len(first_project["sources"]) == 1
        assert Path(first_project["sources"][0]) == Path('src/lib.cpp')
        assert "interface_directories" in first_project
        assert len(first_project["interface_directories"]) == 1
        assert first_project["interface_directories"][0] == 'interface'
        assert "dependencies" not in first_project
        assert "description" not in first_project
        assert "path" not in first_project


def test_new_lib_desc(runtime_dir):
    project_type = "lib"
    project_name = "my_lib"
    project_description = "This is my lib"
    new_project([project_type, project_name, "--desc", project_description])

    # Load the yaml and validate values
    with open(RUNTIME_DIR / project_name / "kiss.yaml" , "r") as f:
        data = yaml.safe_load(f)
        bin_root = data[project_type]
        assert len(bin_root) == 1
        first_project = bin_root[0]
        assert "name" in first_project
        assert first_project["name"] == project_name
        assert "version" in first_project
        assert first_project["version"] == "0.1.0"
        assert "sources" in first_project
        assert len(first_project["sources"]) == 1
        assert Path(first_project["sources"][0]) == Path('src/lib.cpp')
        assert "interface_directories" in first_project
        assert len(first_project["interface_directories"]) == 1
        assert first_project["interface_directories"][0] == 'interface'
        assert "dependencies" not in first_project
        assert "description" in first_project
        assert first_project["description"] == project_description
        assert "path" not in first_project


def test_new_lib_empty(runtime_dir):
    project_type = "lib"
    project_name = "my_lib"
    project_description = "This is my lib"
    new_project([project_type, project_name, "-e", "--desc", project_description])

    # Load the yaml and validate values
    with open(RUNTIME_DIR / project_name / "kiss.yaml" , "r") as f:
        data = yaml.safe_load(f)
        bin_root = data[project_type]
        assert len(bin_root) == 1
        first_project = bin_root[0]
        assert "name" in first_project
        assert first_project["name"] == project_name
        assert "version" in first_project
        assert first_project["version"] == "0.1.0"
        assert "sources" not in first_project
        assert "interface_directories" not in first_project
        assert "dependencies" not in first_project
        assert "description" in first_project
        assert first_project["description"] == project_description
        assert "path" not in first_project