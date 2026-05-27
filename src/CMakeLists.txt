cmake_minimum_required(VERSION 3.6)

set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}" CACHE PATH "Installation directory" FORCE)

project(xlog)

include(../comm/utils.cmake)
include(../comm/CMakeExtraFlags.txt)

# Make `#include "xlog/<name>.h"` resolve to this src directory by mirroring
# its public headers under <build>/include/xlog/.
set(XLOG_FORWARD_INCLUDE_DIR "${CMAKE_CURRENT_BINARY_DIR}/forward_include")
file(MAKE_DIRECTORY "${XLOG_FORWARD_INCLUDE_DIR}/xlog")
foreach(_pub_hdr appender.h xlogger.h xlogger_interface.h xlogger_kmp.h compiler_util.h)
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/${_pub_hdr}"
        "${XLOG_FORWARD_INCLUDE_DIR}/xlog/${_pub_hdr}"
        COPYONLY)
endforeach()

include_directories(.)
include_directories(..)
include_directories(export_include)
include_directories(${XLOG_FORWARD_INCLUDE_DIR})
include_directories(../comm)
include_directories(crypt/micro-ecc-master)

set(SELF_SRC_FILES
    appender.cc
    appender.h
    formater.cc
    log_base_buffer.cc
    log_base_buffer.h
    log_zlib_buffer.cc
    log_zlib_buffer.h
    log_zstd_buffer.cc
    log_zstd_buffer.h
    xlogger_appender.h
    xlogger_interface.cc
    xlogger_interface.h
    xlogger.h
    xlogger_kmp.h
    compiler_util.h
    crypt/log_crypt.cc
    crypt/log_crypt.h
    crypt/log_magic_num.h
    crypt/micro-ecc-master/uECC.c
    crypt/micro-ecc-master/uECC.h
    crypt/micro-ecc-master/types.h
    crypt/micro-ecc-master/uECC_vli.h
)

if(ANDROID)
    list(APPEND SELF_SRC_FILES
        ../comm/xlogger/xloggerbase.c
        ../comm/xlogger/xlogger.cc
        ../platform/android/jni/Java2C_Xlog.cc
        ../platform/android/jni/ConsoleLog.cc
        ../platform/android/jni/JNI_OnLoad.cc
    )
elseif(APPLE)
    list(APPEND SELF_SRC_FILES
        ../platform/ios/objc_console.mm
    )
elseif(OHOS)
    list(APPEND SELF_SRC_FILES
        ../platform/ohos/ConsoleLog.cc
        ../platform/ohos/xlogger_kmp.cc
    )
endif()

add_library(${PROJECT_NAME} STATIC ${SELF_SRC_FILES})
install(TARGETS ${PROJECT_NAME} ARCHIVE DESTINATION ${CMAKE_SYSTEM_NAME}.out)

if(ANDROID)
    get_filename_component(EXPORT_EXP_FILE ../platform/android/jni/export.exp ABSOLUTE)
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,--version-script=${EXPORT_EXP_FILE}")
endif()
