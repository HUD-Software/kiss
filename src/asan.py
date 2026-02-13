from pathlib import Path
import console
from toolchain import Toolchain

def get_msvc_asan_dynamic_lib_path(toolchain: Toolchain) -> list[str]:
    if toolchain.compiler.is_clangcl_based():
        base_path = toolchain.compiler.cxx_path.parent.parent 
        matches = base_path.glob("lib/clang/*/lib/windows/clang_rt.asan_dynamic-x86_64.lib") 
        if(first_match := next(matches, None) ) is None:
            console.print_error("clang_rt.asan_dynamic-x86_64.lib not found in LLVM directories")
            return None
        return str(Path(first_match).resolve().as_posix())
    else:
        console.print_error("clang_rt.asan_dynamic-x86_64.lib not found in LLVM directories because compiler must be a derivate of 'cl' or 'clangcl' ")
        return None

def get_msvc_asan_dynamic_dll_path(toolchain: Toolchain) -> list[str]:
    def find_clang_rt_asan_dynamic_i386_dll(path : Path) -> str | None:
        matches = path.glob("clang_rt.asan_dynamic-i386.dll") 
        if(first_match := next(matches, None) ) is None:
            console.print_error("clang_rt.asan_dynamic-i386.dll not found in MSVC directories")
            console.print_error(f"  {path}")
            return None
        return str(Path(first_match).resolve().as_posix())
    
    def find_clang_rt_asan_dynamic_x86_64_dll(path : Path) -> str | None:
        matches = path.glob("clang_rt.asan_dynamic-x86_64.dll") 
        if(first_match := next(matches, None) ) is None:
            console.print_error("clang_rt.asan_dynamic-x86_64.dll not found in MSVC directories")
            console.print_error(f"  {path}")
            return None
        return str(Path(first_match).resolve().as_posix())
    
    if toolchain.compiler.is_cl_based():
        # CL host is x86_64 bits and target is x86_64
        if toolchain.is_host_x86_64() and toolchain.target.is_x86_64():
            base_path = toolchain.compiler.cxx_path.parent
            return find_clang_rt_asan_dynamic_x86_64_dll(base_path)
        # CL host is x86_64 bits and target is i686
        elif toolchain.is_host_x86_64() and toolchain.target.is_i686():
            base_path = toolchain.compiler.cxx_path.parent.parent / "x86"
            return find_clang_rt_asan_dynamic_i386_dll(base_path)
        else:
            console.print_error("clang_rt.asan_dynamic-*.dll not found in MSVC directories")
            console.print_error(f"Toolchain target architecture is not supported. {toolchain.target.arch}")

    elif toolchain.compiler.is_clangcl_based():
        base_path = toolchain.compiler.parent.parent 
        matches = base_path.glob("lib/clang/*/lib/windows/clang_rt.asan_dynamic-x86_64.dll") 
        if(first_match := next(matches, None) ) is None:
            console.print_error("clang_rt.asan_dynamic-x86_64.dll not found in LLVM directories")
            return None
        return str(Path(first_match).resolve().as_posix())
    else:
        console.print_error("clang_rt.asan_dynamic-x86_64.lib not found in LLVM directories because compiler must be a derivate of 'cl' or 'clangcl' ")
        return None

def get_msvc_asan_dll_thunk_lib_path(toolchain: Toolchain) -> list[str]:
    base_path =  toolchain.compiler.parent.parent 
    matches = base_path.glob("lib/clang/*/lib/windows/clang_rt.asan_dll_thunk-x86_64.lib") 
    if(first_match := next(matches, None) ) is None:
        console.print_error("clang_rt.asan_dynamic_runtime_thunk-x86_64.lib not found in LLVM directories")
        return None
    return str(Path(first_match).resolve().as_posix())