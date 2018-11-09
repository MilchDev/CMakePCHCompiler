cmake_minimum_required(VERSION 3.11)

if(NOT ORIGINAL_SOURCE_DIR)
  set(ORIGINAL_SOURCE_DIR ${CMAKE_SOURCE_DIR})
  message(STATUS "ORIGINAL_SOURCE_DIR not set, defaulting to ${ORIGINAL_SOURCE_DIR}")
endif()

list(APPEND CMAKE_MODULE_PATH ${ORIGINAL_SOURCE_DIR}/../../)
project(pch_test VERSION 0.1 LANGUAGES CXX CXXPCH)

add_library(testlib main.cpp)

if(USE_PRECOMPILED)
  target_precompiled_header(testlib header.h)
endif()