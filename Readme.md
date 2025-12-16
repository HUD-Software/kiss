# Python
Run application with python: `python run.py -d tests list`
VSCode tasks:
- `Build KISS` : Build the binary of kiss
- `Run KISS` : Run the kiss binary

# Deploy
build with `python build.py`

# TOML

## Binary
You can create a binary project that will create a binary *(.exe, elf file)*.
Name should contains `a-z`, `A-Z` and `0-9`
Name should not contains space or special caracter ```@#$%^&*()+={}[].,``
```text
📁 my_binary
└─ 📄 kiss.yaml
```

```yaml
# my_binary/kiss.yaml
bin:
  - name: "my_binary"
    description : "This is my binary project"
    version: "1.0.1"
```

###### Command
```sh
# Created with 
kiss new bin my_binary
# or
kiss new bin my_binary -desc "This is my binary project"
```

## Library:
```text
📁 my_library
└─ 📄 kiss.yaml
```

```yaml
# my_library/kiss.yaml
lib:
  - name: "my_library"
    description : "This is my library"
    version: "0.0.1"
```
###### Command
```sh
# Created with 
kiss new lib my_library
# or
kiss new lib my_library -desc "This is my library"
```

## Dynamic library:
```text
📁 my_dyn_library
└─ 📄 kiss.yaml
```

```yaml
# my_dyn_library/kiss.yaml
dyn:
  - name: "my_dyn_library"
    description : "This is my dynamic library"
    version: "0.0.1"
```
###### Command
```sh
# Created with 
kiss new dyn my_dyn_library
# or
kiss new dyn my_dyn_library -desc "This is my dynamic library"
```

## Multi-project
You can add project inside another project like a bin that use a lib.
You have 2 ways to add a project, you can create a new projet in a separated file (We strongly recommend this), or you can put everything in the same file.
### Separate file
You can add dependencies to other project. In this exemple, *my_binary* needs *my_library*
Note that we need to add the `dependencies` in *my_binary*.
```text
📁 my_binary
├─ 📄 kiss.yaml
│  └─ 📁 my_library
│     └─ 📄 kiss.yaml
```

```yaml
# my_binary/kiss.yaml
bin:
   name: "my_binary"
    description : "This is my binary project"
    version: "0.0.1"
    dependencies : 
      - path : "my_library"
```
```yaml
# my_binary/my_library/kiss.yaml
lib:
  - name: "my_library"
    description : "This is my library project"
    version: "0.0.1"
```
###### Command
```sh
# Create the `my_library` and add it `my_library` as dependencies of `my_binary`
cd my_binary && kiss new my_library && kiss add my_library --path "./my_library"
# or simply
cd my_binary && kiss new my_library && kiss add my_library
```

### Same file
You can add dependencies to other project. In this exemple, *my_binary* needs *my_library*
Note that we need to add the `dependencies` in *my_binary*.
```text
📁 my_binary
├─ 📄 kiss.yaml
└─ 📁 my_library
```

```yaml
# my_binary/kiss.yaml
bin:
  - name: "my_binary"
    description : "This is my binary project"
    version: "0.0.1"
    dependencies : 
      - path : "my_library"
lib:
  - name: "my_library"
    description : "This is my library project"
    version: "0.0.1"
    path: "my_library"
```

###### Command
```sh
# Create the `my_library` and add it `my_library` as dependencies of `my_binary`
cd my_binary && kiss new --existing lib my_library --path "./my_library"
# or simply
cd my_binary && kiss new --existing lib my_library
```
## Workspace
Workspace are special place where you can reference multiple project under 1 big project.
Workspace does not contains code, it contains projects similar to visual studio .sln or VSCode .workspace.

```text
📁 ~/repos
├─ 📁 my_binary
│  ├─ 📄 kiss.yaml
├─ 📁 my_library
│  └─ 📄 kiss.yaml
📁 ~/projects
├─ 📁 my_big_project
│  └─ 📄 kiss.yaml
```

```yaml
# my_big_project/kiss.yaml
workspace:
  name: "my_big_project"
  description : "This is my workspace w"
  version: "0.0.1"
  projects:
    - path: "~/repos/my_binary"
    - path: "../../repos/my_library"
```

###### Command
```sh
# Created with
cd ~/projects
kiss new workspace "my_big_project" -desc "This is my workspace w" -p "./my_binary" "./my_library" "/usr/include/other_lib/"
```

## Managing name collision
Using external project can produce name collision when you request a build of a specific project, let's dive in an exemple:

```text
📁 repos
├─ 📁 my_library
│  └─ 📄 kiss.yaml
├─ 📁 collision
│  └─ 📁 my_library
│      └─ 📄 kiss.yaml
📁 my_big_project
└─ 📄 kiss.yaml
```
```yaml
# my_big_project/kiss.yaml
workspace:
  name: "my_big_project"
  description : "This is my workspace w"
  version: "0.0.1"
  projects:
    - path: "~/repos/my_library"
    - path: "~/repos/collision/my_library"
```

If we try to build the workspace:
```sh
cd my_big_project
kiss build
```
We will get an error because both `~/repos/my_library` and `~/repos/collision/my_library` are referred to as `my_library`.

The same problem occurs when building a specific project:
```sh
cd my_big_project
kiss build my_library
```
`Kiss` does not know which `my_library` you want to build—the one in `~/repos/my_library` or the one in `~/repos/collision/my_library`.

Solution: Use an alias
You can differentiate projects by adding an alias:
```yaml
# my_big_project/kiss.yaml
workspace:
  name: "my_big_project"
  description : "This is my workspace w"
  version: "0.0.1"
  projects:
    - path: "~/repos/my_library"
    - path: "~/repos/collision/my_library"
      alias : collision_my_library
```
Now, `~/repos/collision/my_library` is referred to as `collision_my_library` instead of my_library.

Building the whole workspace works correctly.

You can also build a specific project unambiguously:
```sh
kiss build my_library           # builds ~/repos/my_library
kiss build collision_my_library # builds ~/repos/collision/my_library
```


# Post/pre build command
```yaml
bin:
  - name: "my binary b"
    description : "This is my binary project b"
    version: "1.0.1"
    prebuild:
      interpreter: python
      commands:
        - "print('prebuild {$name}')"
    postbuild:
      interpreter: python
      commands:
        - "print('postbuild {$name}')"
```