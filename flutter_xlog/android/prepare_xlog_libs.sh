#!/usr/bin/env bash
# Build libmarsxlog.so for Android via build_android.py and stage the .so files
# under android/src/main/jniLibs/ so the Android library plugin can pack them
# directly without invoking CMake on every Flutter build.
set -euo pipefail

THIS_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(cd "$THIS_DIR/.." && pwd)"
XLOG_ROOT="$(cd "$PLUGIN_DIR/.." && pwd)"

ABIS=("armeabi-v7a" "arm64-v8a")
LIBS_SRC="$XLOG_ROOT/output/android/libs"
JNI_DEST="$THIS_DIR/src/main/jniLibs"

need_build=0
for abi in "${ABIS[@]}"; do
    if [[ ! -f "$LIBS_SRC/$abi/libmarsxlog.so" ]]; then
        need_build=1
        break
    fi
done

if [[ "$need_build" -eq 1 ]]; then
    echo "[flutter_xlog] building libmarsxlog.so via build_android.py..."
    pushd "$XLOG_ROOT" > /dev/null
    python3 build_android.py "" "${ABIS[@]}"
    popd > /dev/null
fi

# Locate libc++_shared.so from the NDK so consumer apps don't have to ship it
# themselves (parity with the previous externalNativeBuild flow).
host_tag=""
case "$(uname -s)" in
    Darwin) host_tag="darwin-x86_64" ;;
    Linux)  host_tag="linux-x86_64" ;;
    MINGW*|MSYS*|CYGWIN*) host_tag="windows-x86_64" ;;
esac
NDK_ROOT="${NDK_ROOT:-${ANDROID_NDK_HOME:-${ANDROID_NDK_ROOT:-}}}"

abi_triple() {
    case "$1" in
        armeabi-v7a) echo "arm-linux-androideabi" ;;
        arm64-v8a)   echo "aarch64-linux-android" ;;
        x86)         echo "i686-linux-android" ;;
        x86_64)      echo "x86_64-linux-android" ;;
        *) echo "" ;;
    esac
}

for abi in "${ABIS[@]}"; do
    src="$LIBS_SRC/$abi/libmarsxlog.so"
    if [[ ! -f "$src" ]]; then
        echo "[flutter_xlog] ERROR: libmarsxlog.so was not produced at $src"
        exit 1
    fi
    mkdir -p "$JNI_DEST/$abi"
    cp -f "$src" "$JNI_DEST/$abi/libmarsxlog.so"

    stl_dest="$JNI_DEST/$abi/libc++_shared.so"
    if [[ -f "$stl_dest" ]]; then
        continue
    fi
    triple="$(abi_triple "$abi")"
    if [[ -n "$NDK_ROOT" && -n "$host_tag" && -n "$triple" ]]; then
        stl_src="$NDK_ROOT/toolchains/llvm/prebuilt/$host_tag/sysroot/usr/lib/$triple/libc++_shared.so"
        if [[ -f "$stl_src" ]]; then
            cp -f "$stl_src" "$stl_dest"
        else
            echo "[flutter_xlog] WARN: libc++_shared.so not found at $stl_src"
        fi
    else
        echo "[flutter_xlog] WARN: NDK_ROOT not set; skipping libc++_shared.so for $abi"
    fi
done

echo "[flutter_xlog] jniLibs staged at $JNI_DEST"
