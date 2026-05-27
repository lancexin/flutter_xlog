cmake_minimum_required(VERSION 3.6)

set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}" CACHE PATH "Installation directory" FORCE)
message(STATUS "CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}")

# OHOS toolchain sets OHOS_PLATFORM=OHOS but does not set CMAKE_SYSTEM_NAME=Android-style flag,
# so detect via the OHOS variable that the toolchain exports.
if(DEFINED OHOS_PLATFORM AND OHOS_PLATFORM STREQUAL "OHOS")
    set(OHOS TRUE)
endif()

# xlog never links the QUIC stack — disable so that comm's BuildWithUnitTest
# macro stops trying to link the unrelated ANDROMEDA framework on Apple.
if(NOT DEFINED DISABLE_QUIC_PROTOCOL)
    set(DISABLE_QUIC_PROTOCOL ON)
endif()

add_subdirectory(comm comm)
add_subdirectory(boost boost)

option(ZSTD_BUILD_STATIC "BUILD STATIC LIBRARIES" ON)
option(ZSTD_BUILD_SHARED "BUILD SHARED LIBRARIES" OFF)
set(ZSTD_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/zstd")
set(LIBRARY_DIR ${ZSTD_SOURCE_DIR}/lib)
include(GNUInstallDirs)
add_subdirectory(zstd/build/cmake/lib zstd)

add_subdirectory(src xlog)

project(xlog_root)

include(comm/utils.cmake)

set(SELF_LIBS_OUT ${CMAKE_SYSTEM_NAME}.out)

if(ANDROID OR OHOS)
    link_directories(xlog comm boost zstd)

    set(SELF_LIB_NAME marsxlog)
    if(ANDROID)
        set(SELF_SRC_FILES platform/android/jni/import.cc)
        get_filename_component(EXPORT_XLOG_EXP_FILE platform/android/jni/export.exp ABSOLUTE)
    else()
        set(SELF_SRC_FILES platform/ohos/import.cc)
        get_filename_component(EXPORT_XLOG_EXP_FILE platform/ohos/export.exp ABSOLUTE)
    endif()
    add_library(${SELF_LIB_NAME} SHARED ${SELF_SRC_FILES})
    install(TARGETS ${SELF_LIB_NAME} LIBRARY DESTINATION ${SELF_LIBS_OUT}
                                     ARCHIVE DESTINATION ${SELF_LIBS_OUT})

    set(SELF_XLOG_LINKER_FLAG "-Wl,--gc-sections -Wl,--version-script='${EXPORT_XLOG_EXP_FILE}'")

    if(ANDROID_ABI STREQUAL "x86_64" OR ANDROID_ABI STREQUAL "x86")
        set(SELF_XLOG_LINKER_FLAG "${SELF_XLOG_LINKER_FLAG} -Wl,--no-warn-shared-textrel")
    endif()

    if(ANDROID)
        target_link_libraries(${SELF_LIB_NAME} "${SELF_XLOG_LINKER_FLAG}"
                              -Wl,--whole-archive
                              xlog
                              -Wl,--no-whole-archive
                              mars-boost
                              comm
                              libzstd_static
                              liblog.so
                              libz.so)
    elseif(OHOS)
        target_link_libraries(${SELF_LIB_NAME} "${SELF_XLOG_LINKER_FLAG}"
                              -Wl,--whole-archive
                              xlog
                              -Wl,--no-whole-archive
                              mars-boost
                              comm
                              libzstd_static
                              libace_napi.z.so
                              libhilog_ndk.z.so
                              libz.so)
    endif()
endif()
