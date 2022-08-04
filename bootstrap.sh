VERSION=103.0.5060.134

SCRIPT_PATH="$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P)"

if [ -d src ]; then
  echo 'src already exists'.
  exit 1
fi

set -e           # exit when command fails
set -o pipefail  # exit when pipe fails
set -x           # print running command

# Same steps with
# https://source.chromium.org/chromium/infra/infra/+/main:recipes/recipes/build_from_tarball.py

# Download source tarball.
CHROMIUM_URL=https://commondatastorage.googleapis.com/chromium-browser-official/chromium-$VERSION.tar.xz
curl -# $CHROMIUM_URL | tar Jxf -

# Download clang.
LLVM_URL=https://commondatastorage.googleapis.com/chromium-browser-clang/Linux_x64/clang-llvmorg-15-init-10168-gc2a7904a-1.tgz
curl -# $LLVM_URL | tar zxf - --directory chromium-$VERSION/third_party/llvm-build/Release+Asserts

mv chromium-$VERSION src
cd src

# Download sysroot.
./build/linux/sysroot_scripts/install-sysroot.py --arch=amd64

# Download nodejs.
./third_party/node/update_node_binaries

# PATH for ninja and clang.
PATH=$SCRIPT_PATH/depot_tools:$PATH
PATH=$SCRIPT_PATH/src/third_party/llvm-build/Release+Asserts/bin:$PATH

GN_ARGS="is_debug=false
         enable_nacl=false
         use_sysroot=true
         is_official_build=true
         enable_distro_version_check=false
         use_system_libjpeg=true
         use_v8_context_snapshot=false"

# Fix "AssertionError: java only allowed in android builds"
GN_ARGS="$GN_ARGS enable_js_type_check=false"

# Bootstrap gn.
./tools/gn/bootstrap/bootstrap.py --gn-gen-args="$GN_ARGS $EXTRA_GN_ARGS"

# Unbundle libraries.
UNBUNDLE_LIBS="fontconfig freetype libdrm libjpeg libwebp opus snappy"
./build/linux/unbundle/replace_gn_files.py --system-libraries $UNBUNDLE_LIBS
