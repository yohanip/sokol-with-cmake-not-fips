cmake_minimum_required(VERSION 3.27)

project(TrySokol)

set(CMAKE_CXX_STANDARD 20)

if(NOT ANDROID)
    message(STATUS "Creating for desktop")
    
    #multi configurations
    set(CMAKE_CONFIGURATION_TYPES "Debug;Release;MinSizeRel;RelWithDebInfo" CACHE STRING "" FORCE)
    
    add_executable(${PROJECT_NAME} src/main.cpp)

    if(UNIX AND NOT APPLE)
        target_link_libraries(${PROJECT_NAME} PRIVATE 
            X11 Xi Xcursor EGL GL dl pthread m)
    endif()
else()
    add_library(${PROJECT_NAME} SHARED src/main.cpp)

    target_link_libraries(${PROJECT_NAME} PRIVATE
        GLESv3 EGL log android)
endif()

target_include_directories(${PROJECT_NAME} PRIVATE external/sokol shaders)