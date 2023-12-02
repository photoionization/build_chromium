#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import tarfile
import urllib.request

from gn_gen import ROOT_DIR, add_depot_tools_to_path, current_os

CHROMIUM_URL = 'https://github.com/photoionization/chromium_source_tarball/releases/download'

def download_and_extract(url, extract_path):
  def track_progress(members):
    for index, member in enumerate(members):
      if (index + 1) % 5000 == 0:
        print('.', end='', flush=True)
      yield member
  stream = urllib.request.urlopen(url)
  # Set errorlevel=0 because the tarball may include linux symbolic links that
  # do not exist on current platform.
  with tarfile.open(fileobj=stream, mode='r|xz', errorlevel=0) as tar:
    tar.extractall(path=extract_path, members=track_progress(tar))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--revision', help='The revision to checkout')
  parser.add_argument('--tarball-url', help='Path to Chromium source tarball')
  parser.add_argument('--src-dir', help='The path of src dir', default='src')
  args = parser.parse_args()

  if not args.revision and not args.tarball_url:
    print('Must specify either --revision or --tarball-url.')
    return 1

  # Same steps with
  # https://source.chromium.org/chromium/infra/infra/+/main:recipes/recipes/build_from_tarball.py

  if args.revision:
    tarball_url = f'{CHROMIUM_URL}/{args.revision}/chromium-{args.revision}.tar.xz'
  else:
    tarball_url = args.tarball_url

  # Download source tarball.
  if not os.path.isdir(args.src_dir):
    tarball_dir = os.path.basename(tarball_url)[:-7]
    if os.path.isdir(tarball_dir):
      print(f'Unable to download tarball since {tarball_dir} exists.')
      return 1

    print('Download and extract', tarball_dir, end='', flush=True)
    download_and_extract(tarball_url, '.')
    print('Done')

    os.rename(tarball_dir, args.src_dir)

  # Download compilers.
  subprocess.check_call([ sys.executable, 'tools/clang/scripts/update.py' ],
                        cwd=args.src_dir)
  subprocess.check_call([ sys.executable, 'tools/rust/update_rust.py' ],
                        cwd=args.src_dir)

  # Download Linux dependencies.
  if current_os() == 'linux':
    subprocess.check_call([ sys.executable,
                            'build/linux/sysroot_scripts/install-sysroot.py',
                            '--arch', 'amd64' ],
                            cwd=args.src_dir)

if __name__ == '__main__':
  exit(main())
