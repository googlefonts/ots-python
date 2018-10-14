#!/bin/bash
BUILD_ROOT=build
BUILD_DIR=$BUILD_ROOT/meson
SRC_DIR=src/c/ots

meson --unity=on --buildtype=release --strip -Ddebug=true $BUILD_DIR $SRC_DIR
ninja -C $BUILD_DIR $1
