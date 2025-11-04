
import os
from pathlib import Path
from cmake.cmake_directories import CMakeDirectories
from generator import GeneratorRegistry
from kiss_parser import KissParser
from project.bin_project import BinProject
from project.project import Project

@GeneratorRegistry.register("cmake", "Generate cmake CMakeLists.txt")
class GeneratorCMake:
     
    @classmethod
    def add_cli_argument_to_parser(cls, parser: KissParser):
        parser.add_argument("-cov", "--coverage", help="enable code coverage", action='store_const', const=True)
        parser.add_argument("-san", "--sanitizer", help="enable sanitizer", action='store_const', const=True)


    def __init__(self, parser: KissParser):
        self.coverage = getattr(parser, "coverage", False)
        self.sanitizer = getattr(parser, "sanitizer", False)
    def __resolve_sources(self, src_list: list[str], project_directory): 
        import glob
        result = []
        for src in src_list:
            # Nettoyage des caractères d'échappement et normalisation
            clean = src.encode('unicode_escape').decode().replace("\\", "/")

            # Chemin relatif à project_dir si nécessaire
            path = Path(clean)
            if not path.is_absolute():
                path = project_directory / path

            # Converti en str avec / pour glob
            pattern = str(path)

            # Ajouter ** si le motif contient **
            matches = glob.glob(pattern)

            for match in matches:
                result.append(str(Path(match).resolve()).replace("\\", "/"))

        return result
    
    def __generateBin(self, directories:CMakeDirectories, project: BinProject):
        os.makedirs(directories.cmakelists_directory, exist_ok=True)
        # Generate CMakeLists.txt
        normalized_src = self.__resolve_sources(project.src, directories.project_directory)
        src_str = "\n".join(normalized_src)
        with open(os.path.join(directories.cmakelists_directory, "CMakeLists.txt"), "w", encoding="utf-8") as f:
            f.write(f"""cmake_minimum_required(VERSION 3.18)

project({project.name} LANGUAGES CXX )

add_executable({project.name}
{src_str}
)
""")
            

        #if self.coverage:
        self.__generateCoverageCMakeFile(directories)
        self.__generateSanitizerCMakeFile(directories)
                
    
    def __generateCoverageCMakeFile(self, directories:CMakeDirectories):
        filepath = os.path.join(directories.build_directory, "coverage.cmake")
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.__WindowsCheck())
                f.write("\n")
                f.write(self.__MSVCCoverage())

    def __WindowsCheck(self) -> str:
        return \
"""
if(NOT WIN32)
    message(FATAL_ERROR "Windows coverage.cmake should not be used if not Windows OS")
endif()
"""
    def __MSVCCoverage(self) -> str:
        return \
r"""
function(enable_coverage project_name lib_name)
    if(CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
        # Disable compiler batching to fix a clang-cl bug when activate --coverage
        # See: https://developercommunity.visualstudio.com/t/Clang-cl---coverage-option-create-gcno-w/10253777
        set_property(TARGET ${project_name} PROPERTY VS_NO_COMPILE_BATCHING ON)
        set_property(TARGET ${lib_name} PROPERTY VS_NO_COMPILE_BATCHING ON)

        target_compile_options(${project_name} PRIVATE --coverage)
        target_compile_options(${lib_name} PRIVATE --coverage)

        # Add clang lib path to libraries paths
        get_filename_component(CMAKE_CXX_COMPILER_PATH ${CMAKE_CXX_COMPILER} DIRECTORY)
        target_link_directories(${project_name} PRIVATE "${CMAKE_CXX_COMPILER_PATH}\\..\\lib\\clang\\${CMAKE_CXX_COMPILER_VERSION}\\lib\\windows\\")
 		# Need to link manually LLVM Bug 40877
 		# See: https://bugs.llvm.org/show_bug.cgi?id=40877
 		target_link_libraries(${project_name} PRIVATE "clang_rt.profile-x86_64.lib")

        add_custom_command( 
            TARGET ${project_name} POST_BUILD
            COMMAND echo Download Grcov...
            COMMAND Powershell.exe Invoke-WebRequest -Uri https://github.com/mozilla/grcov/releases/latest/download/grcov-x86_64-pc-windows-msvc.zip -OutFile ./grcov-x86_64-pc-windows-msvc.zip
            COMMAND Powershell.exe Expand-Archive -Path ./grcov-x86_64-pc-windows-msvc.zip -DestinationPath . -F
        )

        add_custom_command( 
            TARGET ${project_name} POST_BUILD
            COMMAND echo Start coverage...
            COMMAND ./${VS_CONFIG}/${project_name}.exe
        )
        file(REMOVE coverage.windows.clang.lcov.info)
        add_custom_command( 
            TARGET ${project_name} POST_BUILD
            COMMAND echo Generate HTML report...
            COMMAND ./grcov.exe --llvm -t html -b ./${VS_CONFIG}/ -s ./../../
                    --llvm-path ${CMAKE_CXX_COMPILER_PATH}
                    --branch
                    --keep-only "src/*" 
                    --keep-only "interface/*"
                    --excl-start "^.*LCOV_EXCL_START.*" 
                    --excl-stop "^.*LCOV_EXCL_STOP.*" 
                    --excl-line "\"(\\s*^.*GTEST_TEST\\.*)|(^.*LCOV_EXCL_LINE.*)\"" 
                    --excl-br-start "^.*LCOV_EXCL_START.*" 
                    --excl-br-stop "^.*LCOV_EXCL_STOP.*" 
                    --excl-br-line "\"(\\s*^.*GTEST_TEST\\.*)|(^.*LCOV_EXCL_BR_LINE.*)\"" 
                    -o windows.clang
                    ..
        )

        add_custom_command( 
            TARGET ${project_name} POST_BUILD
            COMMAND echo Generate LCOV report...
            COMMAND ./grcov.exe --llvm -t lcov -b ./${VS_CONFIG}/ -s ./../../
                    --llvm-path ${CMAKE_CXX_COMPILER_PATH}
                    --branch
                    --keep-only "src/*"
                    --keep-only "interface/*"
                    --excl-start "^.*LCOV_EXCL_START.*" 
                    --excl-stop "^.*LCOV_EXCL_STOP.*" 
                    --excl-line "\"(\\s*^.*GTEST_TEST\\.*)|(^.*LCOV_EXCL_LINE.*)\"" 
                    --excl-br-start "^.*LCOV_EXCL_START.*" 
                    --excl-br-stop "^.*LCOV_EXCL_STOP.*" 
                    --excl-br-line "\"(\\s*^.*GTEST_TEST\\.*)|(^.*LCOV_EXCL_BR_LINE.*)\"" 
                    -o coverage.windows.clang.lcov.info
                    ..
        )
    elseif(MSVC)
        set(MSVC_CODECOVERAGE_CONSOLE_PATH "C:\\Program Files\\Microsoft Visual Studio\\2022\\Enterprise\\Common7\\IDE\\Extensions\\Microsoft\\CodeCoverage.Console\\Microsoft.CodeCoverage.Console.exe" CACHE STRING "Path to Microsoft.CodeCoverage.Console.exe")
        find_program(MSVC_CODECOVERAGE_CONSOLE_EXE ${MSVC_CODECOVERAGE_CONSOLE_PATH})
        if(NOT MSVC_CODECOVERAGE_CONSOLE_EXE)
            message(FATAL_ERROR "Code coverage on Windows need Microsoft.CodeCoverage.Console.exe available in Visual Studio 2022 17.3 Enterprise Edition")
        endif()
        message("Enable MSCV coverage with Microsoft.CodeCoverage.Console.exe")

        target_link_options(${project_name} PRIVATE /PROFILE)

        add_custom_command(
            TARGET ${project_name} POST_BUILD
            COMMAND echo Instrument ${project_name}.exe
            COMMAND ${MSVC_CODECOVERAGE_CONSOLE_EXE} instrument ${VS_CONFIG}/${project_name}.exe 
                    --settings ../../coverage.runsettings
        )
        add_custom_command(
            TARGET ${project_name} POST_BUILD
            COMMAND echo Collect ${project_name}.exe
            COMMAND ${MSVC_CODECOVERAGE_CONSOLE_EXE} collect ${VS_CONFIG}/${project_name}.exe 
                    --output ${VS_CONFIG}/coverage.windows.msvc.cobertura 
                    --output-format cobertura 
                    --settings ../../coverage.runsettings
        )
    else()
        message(STATUS "Unsupported compiler")
    endif()
endfunction()
"""

    def __generateSanitizerCMakeFile(self, directories:CMakeDirectories):
        filepath = os.path.join(directories.build_directory, "sanitizer.cmake")
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.__WindowsCheck())
                f.write("\n")
                f.write(self.__MSVCSanitizer())
    
    def __MSVCSanitizer(self) -> str:
        return \
r"""
function(enable_sanitizer project_name lib_name)
	if(MSVC)
		if(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
			get_filename_component(CMAKE_CXX_COMPILER_PATH ${CMAKE_CXX_COMPILER} DIRECTORY)
			if(	NOT EXISTS "${CMAKE_CXX_COMPILER_PATH}/clang_rt.asan_dbg_dynamic-x86_64.dll" OR NOT EXISTS "${CMAKE_CXX_COMPILER_PATH}/clang_rt.asan_dynamic-x86_64.dll")
				message(FATAL_ERROR "MSVC Address Sanitizer is not installed. Please install the C++ AddressSanitizer with Visual Studio Installer")
			endif()
			message("Enable MSCV sanitizer")

			# MSVC ASAN is limited
			# https://devblogs.microsoft.com/cppblog/addresssanitizer-asan-for-windows-with-msvc/#compiling-with-asan-from-the-console
			target_compile_options(${project_name} PRIVATE /fsanitize=address)
			target_compile_options(${lib_name} PRIVATE /fsanitize=address)

			# Disable <vector> ASAN Linker verification 
			# https://learn.microsoft.com/en-us/answers/questions/864574/enabling-address-sanitizer-results-in-error-lnk203
			target_compile_definitions(${project_name} PRIVATE _DISABLE_VECTOR_ANNOTATION)
			target_compile_definitions(${project_name} PRIVATE _DISABLE_STRING_ANNOTATION)

			# Disable incremental (warning LNK4300)
			set_target_properties(${project_name} PROPERTIES LINK_FLAGS "/INCREMENTAL:NO")

			add_custom_command(TARGET ${project_name} POST_BUILD 
				COMMAND Echo "Copy ${CMAKE_CXX_COMPILER_PATH}/clang_rt.asan_dbg_dynamic-x86_64.dll to $<TARGET_FILE_DIR:${project_name}>"
				COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CXX_COMPILER_PATH}/clang_rt.asan_dbg_dynamic-x86_64.dll $<TARGET_FILE_DIR:${project_name}>
				COMMAND Echo "Copy ${CMAKE_CXX_COMPILER_PATH}/clang_rt.asan_dynamic-x86_64.dll to $<TARGET_FILE_DIR:${project_name}>"
				COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CXX_COMPILER_PATH}/clang_rt.asan_dynamic-x86_64.dll $<TARGET_FILE_DIR:${project_name}>
			)
		elseif( CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
			message(WARNING  "ASAN with Clang-cl is not supported")
			# https://github.com/aminya/project_options/issues/138
			# https://stackoverflow.com/questions/66531482/application-crashes-when-using-address-sanitizer-with-msvc
			# https://devblogs.microsoft.com/cppblog/asan-for-windows-x64-and-debug-build-support/
			# https://learn.microsoft.com/en-us/cpp/sanitizers/asan-runtime?view=msvc-170
		endif()
	elseif( CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
		message("Enable sanitizer")
		# https://developers.redhat.com/blog/2021/05/05/memory-error-checking-in-c-and-c-comparing-sanitizers-and-valgrind
		set(SANTIZE_COMPILE_ARGS 
			-fsanitize=address 
			-fsanitize=undefined 
			-fno-sanitize-recover=all
			-fsanitize=float-divide-by-zero
			-fsanitize=float-cast-overflow 
			-fsanitize=alignment
			$<$<CONFIG:Release>:-fno-omit-frame-pointer -g>
			$<$<CONFIG:MinSizeRel>:-fno-omit-frame-pointer -g>
			$<$<CONFIG:RelWithDebInfo>:-fno-omit-frame-pointer -g>
		)
		target_compile_options(${project_name} PRIVATE ${SANTIZE_COMPILE_ARGS})
		target_link_options(${project_name} PRIVATE ${SANTIZE_COMPILE_ARGS})
		target_compile_options(${lib_name} PRIVATE ${SANTIZE_COMPILE_ARGS})
		target_link_options(${lib_name} PRIVATE ${SANTIZE_COMPILE_ARGS})
	endif()
endfunction() 
"""


    def generate(self, args : KissParser, project: Project):
        directories = CMakeDirectories (args, project)
        match project:
            case BinProject():
                self.__generateBin(directories, project)
                
            
    