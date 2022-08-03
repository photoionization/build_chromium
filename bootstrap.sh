VERSION=103.0.5060.134

set -e           # exit when command fails
set -o pipefail  # exit when pipe fails
set -x           # print running command

CHROMIUM_URL=https://commondatastorage.googleapis.com/chromium-browser-official/chromium-$VERSION.tar.xz
curl -# $CHROMIUM_URL | tar Jxf -

mv chromium-$VERSION src
cd src

LLVM_URL=https://commondatastorage.googleapis.com/chromium-browser-clang/Linux_x64/clang-llvmorg-15-init-10168-gc2a7904a-1.tgz
curl -# $LLVM_URL | tar zxf - --directory third_party/llvm-build/Release+Asserts

mkdir -p out/Release
cat >> out/Release/args.gn <<-EOF
  use_sysroot=false
  is_official_build=true
EOF
