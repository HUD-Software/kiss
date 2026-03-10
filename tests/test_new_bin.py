from pathlib import Path

import yaml
from tests.runtime_fixture import runtime_dir, RUNTIME_DIR
from tests.common import new_project, new_inner_project

def test_new_bin_default(runtime_dir):
    project_type = "bin"
    project_name = "my_bin"
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
        assert Path(first_project["sources"][0]) == Path('src/main.cpp')
        assert "dependencies" not in first_project
        assert "description" not in first_project
        assert "path" not in first_project

def test_new_bin_default_inner(runtime_dir):
    project_type = "bin"
    project_name = "my_bin"
    new_project([project_type, project_name])
    project_type = "bin"
    dep_name = "my_bin_2"
    new_inner_project(project_name, ["-e", project_type, dep_name])

    # Load the yaml and validate values
    with open(RUNTIME_DIR / project_name / "kiss.yaml" , "r") as f:
        data = yaml.safe_load(f)
        bin_root = data[project_type]
        assert len(bin_root) == 2
        first_project = bin_root[0]
        assert "name" in first_project
        assert first_project["name"] == project_name
        assert "version" in first_project
        assert first_project["version"] == "0.1.0"
        assert "sources" in first_project
        assert len(first_project["sources"]) == 1
        assert Path(first_project["sources"][0]) == Path('src/main.cpp')
        assert "dependencies" not in first_project
        assert "description" not in first_project
        assert "path" not in first_project
        second_project = bin_root[1]
        assert "name" in second_project
        assert second_project["name"] == dep_name
        assert "version" in second_project
        assert second_project["version"] == "0.1.0"
        assert "sources" in second_project
        assert len(second_project["sources"]) == 1
        assert Path(second_project["sources"][0]) == Path('src/main.cpp')
        assert "dependencies" not in second_project
        assert "description" not in second_project
        assert "path" in second_project
        assert second_project["path"] == dep_name


def test_new_bin_desc(runtime_dir):
    project_type = "bin"
    project_name = "my_bin"
    project_description = "This is my bin"
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
        assert Path(first_project["sources"][0]) == Path('src/main.cpp')
        assert "dependencies" not in first_project
        assert "description" in first_project
        assert first_project["description"] == project_description
        assert "path" not in first_project

def test_new_bin_empty(runtime_dir):
    project_type = "bin"
    project_name = "my_bin"
    project_description = "This is my bin"
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
        assert "dependencies" not in first_project
        assert "description" in first_project
        assert first_project["description"] == project_description
        assert "path" not in first_project
