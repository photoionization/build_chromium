SCRIPT_PATH="$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P)"

set -e           # exit when command fails
set -o pipefail  # exit when pipe fails
set -x           # print running command

PATH=$SCRIPT_PATH/vendor/depot_tools:$PATH

# Build chrome.
TARGET=${1:-content}
ninja -C src/out/Release $TARGET
