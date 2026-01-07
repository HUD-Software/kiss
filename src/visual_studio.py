
from pathlib import Path
import platform
import sys
from typing import Optional
from compiler import Compiler
import console

class Toolset:
    def __init__(self, compiler: Compiler, cxx_compiler_path:str, c_compiler_path:str):
        self.compiler:Compiler=compiler
        self.cxx_compiler_path=cxx_compiler_path
        self.c_compiler_path=c_compiler_path

    @staticmethod
    def get_latest_toolset(compiler:Compiler):
        match platform.system():
            case "Windows":
                return get_windows_latest_toolset(compiler)
            case "Linux":
                print("TBD")
                
    def __str__(self):
        return (f"""compiler={self.compiler}
  cxx={self.cxx_compiler_path},
  c={self.c_compiler_path}""")


class LLVMTools:
    def __init__(self, path: str, profdata: str):
        self.profdata = profdata
        self.path = path

class VSToolset(Toolset):
    def __init__(self, compiler: Compiler, cxx_compiler_path:str, c_compiler_path:str,  major_version:int, product_name:str, product_line_version:int, product_year:int):
        Toolset.__init__(self=self,
                         compiler=compiler,
                         cxx_compiler_path=cxx_compiler_path, 
                         c_compiler_path=c_compiler_path
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

class VSLLVMToolset(VSToolset):
    def __init__(self, compiler: Compiler, cxx_compiler_path:str, c_compiler_path:str,  major_version:int, product_name:str, product_line_version:int, product_year:int, llvm_tools: LLVMTools):
        VSToolset.__init__(self=self,
                           compiler=compiler,
                           cxx_compiler_path=cxx_compiler_path,
                           c_compiler_path=c_compiler_path,
                           major_version=major_version,
                           product_name=product_name,
                           product_line_version=product_line_version,
                           product_year=product_year)
        self.llvm: LLVMTools = llvm_tools

    def __str__(self):
        return (f"VSLLVMToolset(product_name={self.product_name}, "
                f"major_version={self.major_version}, "
                f"cxx={self.cxx_compiler_path}, "
                f"c={self.c_compiler_path})")


def get_windows_latest_toolset(compiler:Compiler) -> Optional[VSToolset] :
    import vswhere
    import json
    latest_installation_path = vswhere.get_latest_path()
    if latest_installation_path:
        latest_major_version = vswhere.get_latest_major_version()
    else:
        latest_installation_path = vswhere.get_latest_path(products='Microsoft.VisualStudio.Product.BuildTools')
        if latest_installation_path:
            latest_major_version = vswhere.get_latest_major_version(products='Microsoft.VisualStudio.Product.BuildTools')
        else:
            console.print_error("Visual Studio is not found.")
            return None
    latest_product_info = vswhere.find(path=latest_installation_path)
    json_str = json.dumps(latest_product_info[0], indent=2)
    json_object = json.loads(json_str)
    json_catalog = json_object["catalog"]
    json_installation_path = Path(json_object["installationPath"])
    match compiler:
        case Compiler.cl:
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
            return VSToolset(compiler=Compiler.cl,
                                cxx_compiler_path=compiler_path / "cl.exe",
                                c_compiler_path=compiler_path / "cl.exe",
                                major_version=latest_major_version,
                                product_name=json_catalog.get('productName'),
                                product_line_version=json_catalog.get('productLineVersion'),
                                product_year=json_catalog.get('featureReleaseYear'))
        case Compiler.clang:
            compiler_path=json_installation_path / "VC\\Tools\\Llvm\\x64\\bin\\"
            return VSLLVMToolset(compiler=Compiler.clang,
                                    cxx_compiler_path=compiler_path / "clang-cl.exe",
                                    c_compiler_path=compiler_path / "clang-cl.exe",
                                    major_version=latest_major_version,
                                    product_name=json_catalog.get('productName'),
                                    product_line_version=json_catalog.get('productLineVersion'),
                                    product_year=json_catalog.get('featureReleaseYear'),
                                    llvm_tools=LLVMTools(path=compiler_path,
                                                        profdata=compiler_path / "llvm-profdata.exe"))
    return None