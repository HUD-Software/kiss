
from pathlib import Path
import sys
from typing import Optional, Self

import console
from toolchain.compiler import Compiler
from toolchain.target import Target


class Toolset:
    def __init__(self, compiler: Compiler):
        self.compiler: Compiler=compiler

    def __str__(self):
        return f"Toolset:\n{self.compiler}"
    

    @staticmethod
    def create(compiler_name: str, target: Target) -> Optional[Self]:
        compiler = Compiler.create(name=compiler_name)
        if not compiler:
            console.print_error(f"Fail to create toolchain with compiler '{compiler_name}'")
            return None
        print(compiler)
        if target.is_windows_os():
            return VSToolset.create(compiler=compiler)
        elif target.is_linux_os():
            return GNUToolset(compiler=compiler)
        console.print_error(f"Unsupported target platform: {target.os}")
        return None


class VSToolset(Toolset):
    def __init__(self, compiler: Compiler, major_version:int, product_name:str, product_line_version:int, product_year:int, installation_path:str):
        Toolset.__init__(self=self, 
                         compiler=compiler)
        self.major_version=major_version
        self.product_name=product_name
        self.product_line_version=product_line_version
        self.product_year=product_year
        self.installation_path=installation_path


    def __str__(self):
        return f"""VSToolset(
  major_version={self.major_version},
  product_name={self.product_name},
  product_line_version={self.product_line_version}
  product_year={self.product_year}
  installation_path={self.installation_path}
)"""
    def create(compiler: Compiler) -> Optional[Self]:
        import vswhere
        # ---------------------------------------------------
        # 🔎 If compiler paths are already set, verify they belong to a valid Visual Studio installation
        # ---------------------------------------------------
        if compiler.cxx_path or compiler.c_path:
            cxx_path = Path(compiler.cxx_path).resolve()

            if compiler.cxx_path != Path() and compiler.c_path != Path() and compiler.cxx_path != compiler.c_path:
                console.print_warning(f"Compiler path 'c_path' and 'cxx_path' are specify in '{compiler.name}' but Visual Studio only use CXX compiler.")
                console.print_warning(f"Ignoring 'c_path'.")

            if not cxx_path.exists():
                console.print_error(f"Compiler path 'cxx_path' {compiler.cxx_path} specify in '{compiler.name}' does not exist.")
                return None

            installations = vswhere.find(find_all=True, products=[
                "Microsoft.VisualStudio.Product.Community",
                "Microsoft.VisualStudio.Product.Professional",
                "Microsoft.VisualStudio.Product.Enterprise",
                "Microsoft.VisualStudio.Product.BuildTools"
            ])

            for installation in installations:
                install_path = Path(installation["installationPath"]).resolve()
                try:
                    cxx_path.relative_to(install_path)
                    
                    
                    # Found matching installation
                    return VSToolset(
                        compiler=compiler,
                        major_version=int(next(iter(installation["installationVersion"].split('.')), '0')),
                        product_name=installation.get("catalog", {}).get("productName"),
                        product_line_version=installation.get("catalog", {}).get("productLineVersion"),
                        product_year=installation.get("catalog", {}).get("featureReleaseYear"),
                        installation_path=install_path
                    )
                except ValueError:
                    continue

            console.print_error(
                f"{cxx_path} does not belong to any detected Visual Studio installation."
            )
            return None

        # ---------------------------------------------------
        # 🔎 If compiler paths are not set, find the first Visual Studio installation
        # ---------------------------------------------------
        import json
        latest_installation_path = vswhere.get_latest_path()
        if latest_installation_path:
            latest_major_version = vswhere.get_latest_major_version()
        else:
            latest_installation_path = vswhere.get_latest_path( products=[
                        "Microsoft.VisualStudio.Product.Community",
                        "Microsoft.VisualStudio.Product.Professional",
                        "Microsoft.VisualStudio.Product.Enterprise",
                        "Microsoft.VisualStudio.Product.BuildTools"
                    ])
            if latest_installation_path:
                latest_major_version = vswhere.get_latest_major_version( products=[
                        "Microsoft.VisualStudio.Product.Community",
                        "Microsoft.VisualStudio.Product.Professional",
                        "Microsoft.VisualStudio.Product.Enterprise",
                        "Microsoft.VisualStudio.Product.BuildTools"
                    ])
            else:
                console.print_error("Visual Studio is not found.")
                return None


        latest_product_info = vswhere.find(path=latest_installation_path)
        json_str = json.dumps(latest_product_info[0], indent=2)
        json_object = json.loads(json_str)
        json_catalog = json_object["catalog"]
        json_installation_path = Path(json_object["installationPath"])
        if compiler.is_cl_based():
            # From https://github.com/microsoft/vswhere/wiki/Find-VC
            vctool_default_version_path = json_installation_path / "VC\\Auxiliary\\Build\\Microsoft.VCToolsVersion.default.txt"
            if vctool_default_version_path.exists():
                vctool_default_version = open(vctool_default_version_path).readline().strip()
            else:
                console.print_error(f"Unable to find Microsoft.VCToolsVersion.default.txt in installation files. \n \
                                            Should be here: {vctool_default_version_path}\n \
                                            Repair Visual studio installation")
                sys.exit(2)
            compiler_path=json_installation_path / f"VC\\Tools\\MSVC\\{vctool_default_version}\\bin\\Hostx64\\x64\\"
            compiler.cxx_path = compiler_path / "cl.exe"
            compiler.c_path = compiler_path / "cl.exe"
            return VSToolset(compiler=compiler,
                            major_version=latest_major_version,
                            product_name=json_catalog.get('productName'),
                            product_line_version=json_catalog.get('productLineVersion'),
                            product_year=json_catalog.get('featureReleaseYear'),
                            installation_path=latest_installation_path)
        elif compiler.is_clangcl_based():
            compiler_path=json_installation_path / "VC\\Tools\\Llvm\\x64\\bin\\"
            compiler.cxx_path = compiler_path / "clang-cl.exe"
            compiler.c_path = compiler_path / "clang-cl.exe"
            return VSToolset(compiler=compiler,
                            major_version=latest_major_version,
                            product_name=json_catalog.get('productName'),
                            product_line_version=json_catalog.get('productLineVersion'),
                            product_year=json_catalog.get('featureReleaseYear'),
                            installation_path=latest_installation_path)
        else:
            console.print_error(f"Unsupported compiler for Visual Studio toolset: {compiler.name}")
        return None

class GNUToolset(Toolset):
    def __init__(self, compiler: Compiler):
        Toolset.__init__(self=self,
                         compiler=compiler
                         )


    def create(compiler: Compiler) -> Optional[Self]:
        if compiler.is_gnu_based():
            # Retrives version of the compiler by running "gcc --version" or "clang --version"
            return GNUToolset(compiler=compiler)
        else:
            console.print_error(f"Unsupported compiler for GNU toolset: {compiler.name}")
        return None