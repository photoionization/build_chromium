#!/usr/bin/env python3

import argparse
import os
import platform
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
SRC_URL = 'https://chromium.googlesource.com/chromium/src.git'

def add_depot_tools_to_path():
  os.environ['DEPOT_TOOLS_UPDATE'] = '0'
  os.environ['CHROMIUM_BUILDTOOLS_PATH'] = os.path.join(SRC_DIR, 'buildtools')
  os.environ['PATH'] = os.pathsep.join([
    os.path.join(SRC_DIR, 'third_party', 'ninja'),
    os.path.join(ROOT_DIR, 'vendor', 'depot_tools'),
  ]) + os.pathsep + os.environ['PATH']

def current_os():
  if sys.platform.startswith('linux'):
    return 'linux'
  elif sys.platform.startswith('win'):
    return 'win'
  elif sys.platform == 'darwin':
    return 'mac'
  else:
    raise ValueError(f'Unsupported platform: {sys.platform}')

def current_cpu():
  arch = platform.machine()
  if arch == 'AMD64' or arch == 'x86_64' or arch == 'x64':
    return 'x64'
  elif arch == 'ARM64':
    return 'arm64'
  elif arch.startswith('ARM'):
    return 'arm'
  else:
    raise ValueError(f'Unrecognized CPU architecture: {arch}')

def gn_gen(dir, args):
  joined_args = ' '.join(args)
  process = subprocess.Popen([ 'gn', 'gen', dir, f'--args={joined_args}'],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, cwd=SRC_DIR)
  for line in process.stdout:
    if '.gclient_entries missing' not in line:
      print(line.strip())
  process.wait()

def main():
  parser = argparse.ArgumentParser(description='Generate GN build config')
  parser.add_argument('--target-cpu', default=current_cpu(),
                      help='Target CPU architecture')
  parser.add_argument('--target-os', default=current_os(),
                      help='Target operating system (win, mac, or linux)')
  parser.add_argument('--arg', action='append', default=[],
                      help='Pass arguments to GN')
  parser.add_argument('--goma', action='store_true', default=False,
                      help='Build with GOMA')
  args = parser.parse_args()

  add_depot_tools_to_path()

  args.arg += [
      'enable_nacl=false',
      f'target_cpu="{args.target_cpu}"',
      f'target_os="{args.target_os}"',
  ]
  if args.goma:
    args.arg += [
        f'import("{ROOT_DIR}/vendor/build_tools/third_party/goma.gn")',
        'use_goma_thin_lto=true',
    ]

  gn_gen('out/Component', args.arg + [
      'is_component_build=true',
      'is_debug=false',
  ])
  gn_gen('out/Release', args.arg + [
      'is_component_build=false',
      'is_debug=false',
      'chrome_pgo_phase=0',
      'is_official_build=true',
      'use_thin_lto=true',
  ])
  gn_gen('out/Debug', args.arg + [
      'is_component_build=true',
      'is_debug=true',
  ])

if __name__ == '__main__':
  main()
