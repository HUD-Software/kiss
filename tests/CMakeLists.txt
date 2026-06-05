cmake_minimum_required(VERSION 3.20)
project(my_bin VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(SOURCES
    src/main.cpp
    src/utils.cpp
)

add_executable(my_bin ${SOURCES})
target_link_libraries(my_bin PRIVATE my_lib my_dll)

# Profile-based compile options
target_compile_options(my_bin PRIVATE
    $<$<CONFIG:Debug>:-Od /Zi>
    $<$<CONFIG:Release>:-O2 /O2>
    $<$<CONFIG:RelWithDebInfo>:-O2 /Zi>
)

# Install rules
install(TARGETS my_bin
)
