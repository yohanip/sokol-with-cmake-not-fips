# Requirements:
- install graphviz
- install clang > 17
- install ninja
- install python > 3.13
- install cmake > 3.27

# how to clone
the simplest
    git clone --branch <tag_name> --depth=1 --recurse-submodules --shallow-submodules <repo_url>
if forgot to recurse-submodule
    git submodule update --init --depth=1 path/to/submodule

# why
trying to build sokol app using vscode in linux + clang++

# steps
1. compile the shader
    python run .py compile-shaders
2. open vs code
3. run by pressing F5 or through the debug panel