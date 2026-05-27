#!/usr/bin/env python3
import glob
import os
import shutil
import sys
import time

from mars_utils import check_ohos_ndk_env, clean, gen_revision_file, get_ohos_strip_cmd, strip_libs


SCRIPT_PATH = os.path.split(os.path.realpath(__file__))[0]

NDK_ROOT = os.environ.get('OHOS_NDK_ROOT', '')

BUILD_OUT_PATH = 'cmake_build/ohos'
LIBS_INSTALL_PATH = BUILD_OUT_PATH + '/'

BUILD_CMD = (
    'cmake %s -DOHOS_ARCH="%s" -DOHOS_PLATFORM=OHOS '
    '-DCMAKE_BUILD_TYPE=Release '
    '-DCMAKE_TOOLCHAIN_FILE=%s/build/cmake/ohos.toolchain.cmake '
    '-DOHOS_STL="c++_shared" '
    '&& cmake --build .'
)

XLOG_SYMBOL_PATH = 'output/ohos/symbols/'
XLOG_LIBS_PATH = 'output/ohos/libs/'

STL_FILE = {
    'armeabi-v7a': NDK_ROOT + '/llvm/lib/arm-linux-ohos/libc++_shared.so',
    'arm64-v8a': NDK_ROOT + '/llvm/lib/aarch64-linux-ohos/libc++_shared.so',
}


def build_ohos(incremental, arch):
    before_time = time.time()

    clean(BUILD_OUT_PATH, incremental)
    os.chdir(BUILD_OUT_PATH)

    build_cmd = BUILD_CMD % (SCRIPT_PATH, arch, NDK_ROOT)
    print('build cmd: ' + build_cmd)
    ret = os.system(build_cmd)
    os.chdir(SCRIPT_PATH)

    if ret != 0:
        print('!!!!!!!!!!!!!!!!!!build fail!!!!!!!!!!!!!!!!!!!!')
        return False

    symbol_path = os.path.join(SCRIPT_PATH, XLOG_SYMBOL_PATH, arch)
    lib_path = os.path.join(SCRIPT_PATH, XLOG_LIBS_PATH, arch)

    if os.path.exists(symbol_path):
        shutil.rmtree(symbol_path)
    os.makedirs(symbol_path)
    if os.path.exists(lib_path):
        shutil.rmtree(lib_path)
    os.makedirs(lib_path)

    for f in glob.glob(LIBS_INSTALL_PATH + '*.so'):
        shutil.copy(f, symbol_path)
        shutil.copy(f, lib_path)

    stl_src = STL_FILE.get(arch)
    if stl_src and os.path.exists(stl_src):
        shutil.copy(stl_src, symbol_path)
        shutil.copy(stl_src, lib_path)
    else:
        print('warning: STL file not found for %s, skipped' % arch)

    strip_libs(get_ohos_strip_cmd(), lib_path)

    print('==================Output========================')
    print('libs(release): %s' % lib_path)
    print('symbols(must store permanently): %s' % symbol_path)
    print('use time: %d s' % int(time.time() - before_time))
    return True


def main(incremental, archs, tag=''):
    if not check_ohos_ndk_env():
        return
    gen_revision_file(SCRIPT_PATH + '/comm', tag)
    for arch in archs:
        if not build_ohos(incremental, arch):
            return


if __name__ == '__main__':
    while True:
        if len(sys.argv) >= 3:
            archs = sys.argv[2:]
            main(False, archs, tag=sys.argv[1])
            break

        archs = ['armeabi-v7a', 'arm64-v8a']
        num = input(
            'Enter menu:\n'
            '1. Clean && build xlog.\n'
            '2. Build incrementally xlog.\n'
            '3. Exit\n'
        )
        if num == '1':
            main(False, archs)
            break
        if num == '2':
            main(True, archs)
            break
        if num == '3':
            break
        main(False, archs)
        break
