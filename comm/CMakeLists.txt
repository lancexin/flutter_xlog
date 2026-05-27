cmake_minimum_required(VERSION 3.6)

set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}" CACHE PATH "Installation directory" FORCE)

project(comm)

include(utils.cmake)
include(CMakeExtraFlags.txt)

include_directories(.)
include_directories(..)
include_directories(assert)
include_directories(thread)
include_directories(xlogger)

set(SELF_SRC_FILES
    autobuffer.cc
    autobuffer.h
    ptrbuffer.cc
    ptrbuffer.h
    strutil.cc
    strutil.h
    tickcount.cc
    tickcount.h
    time_utils.c
    time_utils.h
    verinfo.h
    bootrun.h
    mmap_util.cc
    mmap_util.h
    boost_exception.cc
    compiler_util.h
    string_cast.h
    macro.h
    channel.h
    assert/__assert.h
    assert/__assert.c
    thread/lock.h
    thread/condition.h
    thread/thread.h
    thread/mutex.h
    thread/spinlock.h
    thread/atomic_oper.h
    thread/runnable.h
    xlogger/xloggerbase.h
    xlogger/xloggerbase.c
    xlogger/xlogger.h
    xlogger/xlogger.cc
    xlogger/xlogger_category.h
    xlogger/xlogger_category.cc
    xlogger/loginfo_extract.h
    xlogger/loginfo_extract.c
    xlogger/preprocessor.h
    xlogger/android_xlog.h
)

if(ANDROID)
    add_definitions(-DUSING_XLOG_WEAK_FUNC)
    list(APPEND SELF_SRC_FILES
        jni/util/comm_function.cc
        jni/util/comm_function.h
        jni/util/scope_jenv.cc
        jni/util/scope_jenv.h
        jni/util/scoped_jstring.cc
        jni/util/scoped_jstring.h
        jni/util/var_cache.cc
        jni/util/var_cache.h
        unix/xlogger_threadinfo.cc
        unix/thread/thread.h
        unix/thread/lock.h
        unix/thread/condition.h
        unix/thread/mutex.h
    )
elseif(APPLE)
    list(APPEND SELF_SRC_FILES
        objc/data_protect_attr.h
        objc/data_protect_attr.mm
        objc/scope_autoreleasepool.h
        objc/scope_autoreleasepool.mm
        unix/xlogger_threadinfo.cc
        unix/thread/thread.h
    )
elseif(OHOS)
    list(APPEND SELF_SRC_FILES
        unix/xlogger_threadinfo.cc
        unix/thread/thread.h
        unix/thread/lock.h
        unix/thread/condition.h
        unix/thread/mutex.h
    )
endif()

BuildWithUnitTest("${PROJECT_NAME}" "${SELF_SRC_FILES}")
