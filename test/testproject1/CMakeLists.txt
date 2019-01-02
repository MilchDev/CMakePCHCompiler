cmake_minimum_required(VERSION 3.12)

if(NOT ORIGINAL_SOURCE_DIR)
  set(ORIGINAL_SOURCE_DIR ${CMAKE_SOURCE_DIR})
  message(STATUS "ORIGINAL_SOURCE_DIR not set, defaulting to ${ORIGINAL_SOURCE_DIR}")
endif()

list(APPEND CMAKE_MODULE_PATH ${ORIGINAL_SOURCE_DIR}/../../)
project(pch_test VERSION 0.1 LANGUAGES CXX CXXPCH)

add_library(testotherlib lib/lib.cpp)
target_include_directories(testotherlib PUBLIC lib)
add_library(testlib main.cpp)
target_link_libraries(testlib PRIVATE testotherlib)

if(USE_PRECOMPILED)
  target_precompiled_header(testlib header.h)
endif()