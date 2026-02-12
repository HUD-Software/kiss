
from pathlib import Path
import platform
import sys
from typing import Optional
import console
from toolchain import Compiler, compiler

class Toolset:
    def __init__(self, compiler: Compiler):
        self.compiler:Compiler=compiler

    def __str__(self):
        return f"Toolset:\n{self.compiler}"


class VSToolset(Toolset):
    def __init__(self, compiler: Compiler, major_version:int, product_name:str, product_line_version:int, product_year:int):
        Toolset.__init__(self=self,
                         compiler=compiler
                         )
        self.major_version=major_version
        self.product_name=product_name
        self.product_line_version=product_line_version
        self.product_year=product_year

    def __str__(self):
        base_str = super().__str__()
        return f"""VSToolset(
  {base_str},
  major_version={self.major_version},
  product_name={self.product_name},
  product_line_version={self.product_line_version}
  product_year={self.product_year}
)"""


def get_windows_latest_toolset(compiler:Compiler) -> Optional[VSToolset] :
    import vswhere
    # ---------------------------------------------------
    # 🔎 If compiler paths are already set, verify they belong to a valid Visual Studio installation
    # ---------------------------------------------------
    if compiler.cxx_path != Path() or compiler.c_path != Path():
        cxx_path = Path(compiler.cxx_path).resolve()

        if compiler.cxx_path != Path() and compiler.c_path != Path():
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
                    major_version=installation.get("catalog", {}).get("productLineVersion"),
                    product_name=installation.get("catalog", {}).get("productName"),
                    product_line_version=installation.get("catalog", {}).get("productLineVersion"),
                    product_year=installation.get("catalog", {}).get("featureReleaseYear")
                )
            except ValueError:
                continue

        console.print_error(
            f"{cxx_path} does not belong to any detected Visual Studio installation."
        )
        return None

    
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
    if compiler.is_derived_from("cl"):
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
                         product_year=json_catalog.get('featureReleaseYear'))
    elif compiler.is_derived_from("clangcl"):
        compiler_path=json_installation_path / "VC\\Tools\\Llvm\\x64\\bin\\"
        compiler.cxx_path = compiler_path / "clang-cl.exe"
        compiler.c_path = compiler_path / "clang-cl.exe"
        return VSToolset(compiler=compiler,
                             major_version=latest_major_version,
                             product_name=json_catalog.get('productName'),
                             product_line_version=json_catalog.get('productLineVersion'),
                             product_year=json_catalog.get('featureReleaseYear'))
    return None