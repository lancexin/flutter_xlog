#!/usr/bin/env python3
import os
import shutil
import sys

from mars_utils import (
    XLOG_EXPORT_HEADER_FILES,
    clean,
    export_headers,
    gen_revision_file,
    libtool_libs,
    lipo_libs,
)


SCRIPT_PATH = os.path.split(os.path.realpath(__file__))[0]

BUILD_OUT_PATH = 'cmake_build/iOS'
INSTALL_PATH = BUILD_OUT_PATH + '/iOS.out'

IOS_DEPLOYMENT_TARGET = '13.0'

IOS_BUILD_SIMULATOR_CMD = (
    'cmake ../.. -DCMAKE_BUILD_TYPE=Release '
    '-DCMAKE_TOOLCHAIN_FILE=../../ios.toolchain.cmake '
    '-DPLATFORM=SIMULATOR -DENABLE_ARC=0 -DENABLE_BITCODE=0 -DENABLE_VISIBILITY=1 '
    '-DDEPLOYMENT_TARGET=' + IOS_DEPLOYMENT_TARGET + ' '
    '-DCMAKE_C_FLAGS=-mios-simulator-version-min=' + IOS_DEPLOYMENT_TARGET + ' '
    '-DCMAKE_CXX_FLAGS=-mios-simulator-version-min=' + IOS_DEPLOYMENT_TARGET + ' '
    '&& make -j8 && make install'
)
IOS_BUILD_OS_CMD = (
    'cmake ../.. -DCMAKE_BUILD_TYPE=Release '
    '-DCMAKE_TOOLCHAIN_FILE=../../ios.toolchain.cmake '
    '-DPLATFORM=OS -DENABLE_ARC=0 -DENABLE_BITCODE=0 -DENABLE_VISIBILITY=1 '
    '-DDEPLOYMENT_TARGET=' + IOS_DEPLOYMENT_TARGET + ' '
    '-DCMAKE_C_FLAGS=-mios-version-min=' + IOS_DEPLOYMENT_TARGET + ' '
    '-DCMAKE_CXX_FLAGS=-mios-version-min=' + IOS_DEPLOYMENT_TARGET + ' '
    '&& make -j8 && make install'
)


def build_ios(tag=''):
    gen_revision_file(SCRIPT_PATH + '/comm', tag)

    clean(BUILD_OUT_PATH)
    os.chdir(BUILD_OUT_PATH)
    ret = os.system(IOS_BUILD_OS_CMD)
    os.chdir(SCRIPT_PATH)
    if ret != 0:
        print('!!!!!!!!!!! build os fail !!!!!!!!!!!!!!!')
        return False

    libtool_os_dst_lib = INSTALL_PATH + '/os'
    src_libs = [
        INSTALL_PATH + '/libcomm.a',
        INSTALL_PATH + '/libmars-boost.a',
        INSTALL_PATH + '/libxlog.a',
        BUILD_OUT_PATH + '/zstd/libzstd.a',
    ]
    if not libtool_libs(src_libs, libtool_os_dst_lib):
        return False

    clean(BUILD_OUT_PATH)
    os.chdir(BUILD_OUT_PATH)
    ret = os.system(IOS_BUILD_SIMULATOR_CMD)
    os.chdir(SCRIPT_PATH)
    if ret != 0:
        print('!!!!!!!!!!! build simulator fail !!!!!!!!!!!!!!!')
        return False

    libtool_simulator_dst_lib = INSTALL_PATH + '/simulator'
    if not libtool_libs(src_libs, libtool_simulator_dst_lib):
        return False

    dst_lib = INSTALL_PATH + '/libxlog.a'
    if not lipo_libs([libtool_os_dst_lib, libtool_simulator_dst_lib], dst_lib):
        return False

    dst_headers = INSTALL_PATH + '/include'
    export_headers(XLOG_EXPORT_HEADER_FILES, dst_headers, SCRIPT_PATH)

    print('==================Output========================')
    print('static lib : ' + dst_lib)
    print('headers    : ' + dst_headers)
    return True


def main():
    if len(sys.argv) >= 2:
        build_ios(sys.argv[1])
        return

    while True:
        num = input('Enter menu:\n1. Clean && build xlog.\n2. Exit\n')
        if num == '1':
            build_ios()
            return
        if num == '2':
            return
        build_ios()
        return


if __name__ == '__main__':
    main()
