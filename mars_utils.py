#!/usr/bin/env python3
import glob
import hashlib
import os
import shutil
import subprocess
import time
from typing import Dict, List


XLOG_COPY_HEADER_FILES = {
    "comm/verinfo.h": "comm",
    "comm/autobuffer.h": "comm",
    "comm/time_utils.h": "comm",
    "comm/strutil.h": "comm",
    "comm/string_cast.h": "comm",
    "comm/objc/scope_autoreleasepool.h": "comm",
    "comm/xlogger/preprocessor.h": "xlog",
    "comm/xlogger/xloggerbase.h": "xlog",
    "comm/xlogger/xlogger.h": "xlog",
    "src/appender.h": "xlog",
    "src/xlogger_interface.h": "xlog",
    "src/xlogger_kmp.h": "xlog",
}


# When exporting raw headers (.a integration), we keep the on-disk path the same
# as the include directives written in the source so users only need to add a
# single -I to the include root. xlogger_interface.h does
# `#include "xlogger/xloggerbase.h"`, xlogger.h does `#include "preprocessor.h"`
# and `#include "comm/string_cast.h"`, so we mirror that layout.
XLOG_EXPORT_HEADER_FILES = {
    "comm/verinfo.h": "comm/verinfo.h",
    "comm/autobuffer.h": "comm/autobuffer.h",
    "comm/time_utils.h": "comm/time_utils.h",
    "comm/strutil.h": "comm/strutil.h",
    "comm/string_cast.h": "comm/string_cast.h",
    "comm/objc/scope_autoreleasepool.h": "comm/objc/scope_autoreleasepool.h",
    "comm/xlogger/preprocessor.h": "xlogger/preprocessor.h",
    "comm/xlogger/xloggerbase.h": "xlogger/xloggerbase.h",
    "comm/xlogger/xlogger.h": "xlogger/xlogger.h",
    "src/appender.h": "appender.h",
    "src/xlogger_interface.h": "xlogger_interface.h",
    "src/xlogger_kmp.h": "xlogger_kmp.h",
}


def remove_cmake_files(path):
    cmake_files = path + '/CMakeFiles'
    if os.path.exists(cmake_files):
        shutil.rmtree(cmake_files)
    make_file = path + '/Makefile'
    if os.path.isfile(make_file):
        os.remove(make_file)
    cmake_cache = path + '/CMakeCache.txt'
    if os.path.isfile(cmake_cache):
        os.remove(cmake_cache)
    for f in glob.glob(path + '/*.a'):
        os.remove(f)
    for f in glob.glob(path + '/*.so'):
        os.remove(f)


def clean(path, incremental=False):
    if not incremental:
        for fpath, dirs, fs in os.walk(path):
            remove_cmake_files(fpath)
    if not os.path.exists(path):
        os.makedirs(path)


def is_different_file(file1: str, file2: str) -> bool:
    assert os.path.exists(file1)
    if not os.path.exists(file2):
        return True
    md51 = hashlib.md5(open(file1, 'rb').read()).hexdigest()
    md52 = hashlib.md5(open(file2, 'rb').read()).hexdigest()
    return md51 != md52


def copy_file(src, dst):
    assert os.path.isfile(src), src
    parent = os.path.dirname(dst)
    if parent and not os.path.exists(parent):
        os.makedirs(parent)
    if is_different_file(src, dst):
        shutil.copy(src, dst)


def libtool_libs(src_libs, dst_lib):
    src_lib_str = ' '.join(src_libs)
    print(src_lib_str)
    ret = os.system('libtool -static -no_warning_for_no_symbols -o %s %s' % (dst_lib, src_lib_str))
    if ret != 0:
        print('!!!!!!!!!!!libtool %s fail!!!!!!!!!!!!!!!' % dst_lib)
        return False
    return True


def lipo_libs(src_libs, dst_lib):
    cmd = 'lipo -create %s -output %s' % (' '.join(src_libs), dst_lib)
    ret = os.system(cmd)
    if ret != 0:
        print('!!!!!!!!!!!lipo_libs %s fail, cmd:%s!!!!!!!!!!!!!!!' % (dst_lib, cmd))
        return False
    return True


def make_static_framework(src_lib, dst_framework, header_file_mappings, header_files_src_base='./'):
    if os.path.exists(dst_framework):
        shutil.rmtree(dst_framework)
    os.makedirs(dst_framework)
    shutil.copy(src_lib, dst_framework)
    framework_path = dst_framework + '/Headers'
    for src, dst in header_file_mappings.items():
        copy_file(os.path.join(header_files_src_base, src),
                  os.path.join(framework_path, dst, src[src.rfind('/') + 1:]))
    return True


def export_headers(header_file_mappings, dst_headers_dir, header_files_src_base='./'):
    """Copy headers preserving the include-path layout.

    `header_file_mappings` maps `source_relative_path` → `dest_relative_path`
    (the latter is the path relative to `dst_headers_dir`). This is different
    from `make_static_framework`, which only takes a destination *directory*.
    """
    if os.path.exists(dst_headers_dir):
        shutil.rmtree(dst_headers_dir)
    os.makedirs(dst_headers_dir)
    for src, dst in header_file_mappings.items():
        copy_file(os.path.join(header_files_src_base, src),
                  os.path.join(dst_headers_dir, dst))
    return True


def check_ndk_env():
    ndk_path = os.environ.get('NDK_ROOT', '')
    if not ndk_path:
        print('Error: NDK_ROOT not set.')
        return False
    print('ndk path:%s' % ndk_path)
    if not os.path.isfile(os.path.join(ndk_path, 'source.properties')):
        print("Error: source.properties does not exist.")
        return False
    return True


def _ndk_host_tag():
    import platform as _platform
    system = _platform.system()
    machine = _platform.machine().lower()
    if system == 'Darwin':
        return 'darwin-x86_64'
    if system == 'Linux':
        return 'linux-x86_64'
    if system == 'Windows':
        return 'windows-x86_64' if machine.endswith('64') else 'windows'
    return 'linux-x86_64'


def get_android_strip_cmd():
    ndk_path = os.environ.get('NDK_ROOT', '')
    if not ndk_path:
        return ''
    candidate = os.path.join(
        ndk_path, 'toolchains', 'llvm', 'prebuilt', _ndk_host_tag(), 'bin', 'llvm-strip'
    )
    if os.path.isfile(candidate):
        return candidate
    if os.path.isfile(candidate + '.exe'):
        return candidate + '.exe'
    print('warning: llvm-strip not found under %s' % candidate)
    return ''


def get_ohos_strip_cmd():
    ndk_path = os.environ.get('OHOS_NDK_ROOT', '')
    if not ndk_path:
        return ''
    for rel in (
        os.path.join('llvm', 'bin', 'llvm-strip'),
        os.path.join('build-tools', 'cmake', 'llvm', 'bin', 'llvm-strip'),
    ):
        candidate = os.path.join(ndk_path, rel)
        if os.path.isfile(candidate):
            return candidate
        if os.path.isfile(candidate + '.exe'):
            return candidate + '.exe'
    print('warning: llvm-strip not found under %s' % ndk_path)
    return ''


def strip_libs(strip_cmd, lib_dir):
    if not strip_cmd:
        print('warning: strip skipped, no strip cmd available')
        return
    for f in glob.glob(os.path.join(lib_dir, '*.so')):
        ret = os.system('%s --strip-unneeded %s' % (strip_cmd, f))
        if ret != 0:
            print('warning: strip failed for %s' % f)


def check_ohos_ndk_env():
    ndk_path = os.environ.get('OHOS_NDK_ROOT', '')
    if not ndk_path:
        print('Error: OHOS_NDK_ROOT not set.')
        return False
    print('ohos ndk path:%s' % ndk_path)
    return True


def gen_revision_file(version_file_path, tag=''):
    curdir = os.getcwd()
    os.chdir(version_file_path)
    revision = os.popen('git rev-parse --short HEAD').read().strip()
    branch = os.popen('git rev-parse --abbrev-ref HEAD').read().strip()
    os.chdir(curdir)

    timestamp = int(time.time())
    build_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

    contents = '''
#ifndef Mars_verinfo_h
#define Mars_verinfo_h

#define MARS_REVISION "%s"
#define MARS_PATH "%s"
#define MARS_URL ""
#define MARS_BUILD_TIME "%s"
#define MARS_TAG "%s"
#define MARS_BUILD_TIMESTAMP %u

#endif
''' % (revision, branch, build_time, tag, timestamp)

    with open('%s/verinfo.h' % version_file_path, 'wb') as f:
        f.write(contents.encode())
        f.flush()
