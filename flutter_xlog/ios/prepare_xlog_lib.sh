#!/usr/bin/env bash
# Build libxlog.a + headers from xlog/ and stage them under ios/xlog/ so the
# CocoaPods spec's vendored_libraries entry can pick them up. The artifacts are
# cached at the staged location so subsequent `pod install` runs are no-ops.
set -euo pipefail

THIS_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(cd "$THIS_DIR/.." && pwd)"
XLOG_ROOT="$(cd "$PLUGIN_DIR/.." && pwd)"
LIB_OUT="$XLOG_ROOT/cmake_build/iOS/iOS.out/libxlog.a"
HEADERS_OUT="$XLOG_ROOT/cmake_build/iOS/iOS.out/include"
DEST_DIR="$THIS_DIR/xlog"
DEST_LIB="$DEST_DIR/libxlog.a"
DEST_HEADERS="$DEST_DIR/include"

# Skip everything if artifacts are already staged for this plugin.
if [[ -f "$DEST_LIB" && -d "$DEST_HEADERS" ]]; then
    echo "[flutter_xlog] libxlog.a already staged at $DEST_LIB, skipping"
    exit 0
fi

if [[ ! -f "$LIB_OUT" || ! -d "$HEADERS_OUT" ]]; then
    echo "[flutter_xlog] building libxlog.a via build_ios.py..."
    pushd "$XLOG_ROOT" > /dev/null
    echo 1 | python3 build_ios.py
    popd > /dev/null
fi

if [[ ! -f "$LIB_OUT" || ! -d "$HEADERS_OUT" ]]; then
    echo "[flutter_xlog] ERROR: libxlog.a or headers not produced under $XLOG_ROOT/cmake_build/iOS/iOS.out"
    exit 1
fi

mkdir -p "$DEST_DIR"
rm -rf "$DEST_LIB" "$DEST_HEADERS"
cp "$LIB_OUT" "$DEST_LIB"
cp -R "$HEADERS_OUT" "$DEST_HEADERS"
echo "[flutter_xlog] libxlog.a staged at $DEST_LIB"
echo "[flutter_xlog] headers staged at $DEST_HEADERS"
