import os
import importlib.util
import sys
from pathlib import Path
import subprocess
import argparse
import re
import shutil

project_name: str = "something"

def import_from_path(module_name, file_path):
    file_path = Path(file_path).resolve()
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def compile_shader(dir):
    exe = ".exe" if sys.platform == "win32" else ""
    shdc = os.path.join("external/sokol-tools-bin/bin", sys.platform, "sokol-shdc" + exe)
    exit_code = 1

    print(f"shdc {shdc}")

    def recursive(root, sub):
        print(f">>> entering {root}/{sub}")
                
        current = os.path.join(root, sub)
        for f in os.listdir(current):
            file = os.path.join(current, f)
            
            if os.path.isdir(file):
                exit_code = recursive(current, f)
                if exit_code != 0:
                    return exit_code
            
            [fname, fext] = os.path.splitext(f)
            
            if fext == ".glsl":
                print(f"compiling {fname} of {fext}")

                slangs = ["glsl410", "glsl430", "glsl300es", "glsl310es", "hlsl4", "wgsl"]

                for slang in slangs:
                    print(f"compiling {fname} for {slang}")
                    exit_code = go_subprocess([
                        shdc,
                        "--input", file,
                        "--output", os.path.join(current, fname + "." + slang + ".h"),
                        "--slang", slang
                    ])

                    if exit_code != 0:
                        print(f"failed compiling {fname} for {slang}")
                        return exit_code

        return 0

    if os.path.exists(shdc):
        if os.path.isdir(dir):
            recursive(dir, "")
            # return go_subprocess([shdc])
    return exit_code

def go_subprocess(cmd):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Merge stdout and stderr
        text=True,  # Automatically decode bytes to string
        bufsize=1,  # Line buffering (important for real-time output)
    )

    # Read output line-by-line in real time
    for line in iter(process.stdout.readline, ''):
        print(line, end='')  # Print without extra newlines

    # Ensure process finishes
    process.stdout.close()
    return process.wait()

def read_cmake_file():
    global project_name
    with open("CMakeLists.txt", "r") as f:
        # find project name using regex
        for line in f:
            #regex
            match = re.match(r"project\((.*?)\)", line, re.IGNORECASE)
            if match:
                project_name = match.group(1)
                break
        
def clean():
    if os.path.exists("build"):
        for entry in os.listdir("build"):
            if entry == "_deps":
                # not deleting deps..
                continue
            file = os.path.join("build", entry)
            if os.path.isfile(file):
                os.unlink(file)
            elif os.path.isdir(file):
                shutil.rmtree(file)
    return 0
                
def build_tools():
    # run the command
    exit_code = go_subprocess([
        "cmake",
        "-B", "build-tools",
        # "-DPLAYSDL_BUILD_TOOLS=ON"
    ])
    
    if exit_code == 0:
        exit_code = go_subprocess([
            "cmake",
            "--build", "build-tools"
        ])

    return exit_code


def configure(open=False, clean=False):
    cmd = [
        "cmake",
        "-B", "build",
        # "-DPLAYSDL_BUILD_TOOLS=OFF"
    ]

    if sys.platform == "win32":
        cmd += ["-G", "Visual Studio 17 2022", "-T", "ClangCL"]
    else:
        cmd += ["-G", "Ninja Multi-Config", "-DCMAKE_C_COMPILER=clang", "-DCMAKE_CXX_COMPILER=clang++"]

    if clean:
        if os.path.exists("build/CMakeCache.txt"):
            os.unlink("build/CMakeCache.txt")

    # run the command
    exit_code = go_subprocess(cmd)
    
    # open sln file
    if exit_code == 0 and open:
        if sys.platform == "win32":
            target = os.path.abspath(os.path.join("build", f"{project_name}.sln"))
            if os.path.exists(target):
                os.startfile(target)
            else:
                print(f"could not find solution file {target}")
        else:
            print("only windows could not open solution file")
    
    return exit_code

def build(release=False, clean_config=False):
    exit_code = configure(clean=clean_config)
    if exit_code != 0:
        sys.exit(exit_code)

    exit_code = go_subprocess([
        "cmake",
        "--build", "build",
        "--config", "MinSizeRel" if release else "Debug"
    ])
    
    if exit_code == 0:
        os.chdir("build")
        
        # generate graphviz
        ec = go_subprocess([
            "cmake",
            "--graphviz", "dependencies.dot", "."
        ])
        
        if ec == 0:
            go_subprocess([
                "dot",
                "-Tpng",
                "dependencies.dot",
                "-o", "../cmake-dependencies-windows.png"
            ])

        os.chdir("..")

    return exit_code

if __name__ == "__main__":
    # make sure the working directory is the root folder..
    if not os.path.isdir(".venv"):
        # try to change dir to the root folder
        os.chdir("..")
        if not os.path.isdir(".venv"):
            # if it still doesn't exist, exit
            print("This script must be run from the root folder where .venv is")
            sys.exit(1)
            
    read_cmake_file()
        
    parser = argparse.ArgumentParser(description="Build system with configure step.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    build_tools_parser = subparsers.add_parser("build-tools", help="Build the tools")
    
    # Configure command
    config_parser = subparsers.add_parser("configure", help="Configure the project")
    config_parser.add_argument("--open", action="store_true", help="Open the editor after configuring")
    config_parser.add_argument("--clean", action="store_true", help="clean configuration")
    
    # Build command (default)
    build_parser = subparsers.add_parser("build", help="Build the project (runs configure automatically)")
    build_parser.add_argument("-r", "--release", action="store_true", help="build a release version")
    build_parser.add_argument("-cc", "--clean-config", action="store_true", help="clean the configuration")

    # Shader Compile
    shader_parser = subparsers.add_parser("compile-shaders", help="Build shader for sokol")
    shader_parser.add_argument("-d", "--dir", default="shaders", help="the directoy to build")
    
    # clean
    clean_parser = subparsers.add_parser("clean", help="Clean the build folder")
    
    # Parse arguments
    args = parser.parse_args()
  
    exit_code = 0
  
    # Execute commands
    if args.command == "configure":
        exit_code = configure(open = args.open, clean=args.clean)
    elif args.command == "build":
        exit_code = build(release=args.release, clean_config=args.clean_config)
    elif args.command == "clean":
        exit_code = clean()
    elif args.command == "build-tools":
        exit_code = build_tools()
    elif args.command == "compile-shaders":
        exit_code = compile_shader(args.dir)
    else:
        # show help
        parser.print_help()
        sys.exit(1)
    
    print("===============================================DONE!===============================================")
    sys.exit(exit_code)
