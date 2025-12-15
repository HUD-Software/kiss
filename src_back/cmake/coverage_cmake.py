import os
from cmake.cmake_directories import CMakeDirectories


def generateCoverageCMakeFile(self, directories:CMakeDirectories):
    filepath = directories.build_directory / "coverage.cmake"
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.__windowsCheckStr())
            f.write("\n")
            f.write(self.__MSVCCoverageStr())

def __windowsCheckStr(self) -> str:
    return \
"""
if(NOT WIN32)
    message(FATAL_ERROR "Windows coverage.cmake should not be used if not Windows OS")
endif()
"""

def __MSVCCoverageStr(self) -> str:
    return \
r"""function(enable_coverage project_name lib_name)
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

