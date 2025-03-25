cmake_minimum_required(VERSION 3.27)

project(TrySokol)

set(CMAKE_CXX_STANDARD 20)

add_executable(${PROJECT_NAME} src/main.cpp)

target_include_directories(${PROJECT_NAME} PRIVATE external/sokol shaders)
target_link_libraries(${PROJECT_NAME} PRIVATE X11 Xi Xcursor EGL GL dl pthread m)