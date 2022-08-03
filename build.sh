# Same steps with
# https://source.chromium.org/chromium/infra/infra/+/main:recipes/recipes/build_from_tarball.py

SCRIPT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

set -e           # exit when command fails
set -o pipefail  # exit when pipe fails
set -x           # print running command

cd src

PATH=$SCRIPT_PATH/depot_tools:$PATH
PATH=$SCRIPT_PATH/src/third_party/llvm-build/Release+Asserts/bin:$PATH
GN_ARGS="is_debug=false
         enable_nacl=false
         use_sysroot=true
         is_official_build=true
         enable_distro_version_check=false
         use_system_libjpeg=true
         use_v8_context_snapshot=false"
UNBUNDLE_LIBS="fontconfig
               freetype
               libdrm
               libjpeg
               libwebp
               opus
               snappy"

# Fix "AssertionError: java only allowed in android builds"
GN_ARGS="$GN_ARGS enable_js_type_check=false"

# Use ccache.
GN_ARGS="$GN_ARGS cc_wrapper=\"env CCACHE_SLOPPINESS=time_macros ccache\""

# Bootstrap gn.
./tools/gn/bootstrap/bootstrap.py --gn-gen-args="$GN_ARGS"

# Unbundle libraries.
./build/linux/unbundle/replace_gn_files.py --system-libraries $UNBUNDLE_LIBS

# Build chrome.
ninja -C out/Release content
