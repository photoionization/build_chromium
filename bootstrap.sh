VERSION=103.0.5060.134

set -e           # exit when command fails
set -o pipefail  # exit when pipe fails
set -x           # print running command

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
