#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys

from gn_gen import SRC_DIR, add_depot_tools_to_path, current_os

def use_goma(args):
  with open(os.path.join(args.out_dir, 'args.gn'), 'r') as f:
    return 'goma.gn' in f.read()

def main():
  parser = argparse.ArgumentParser(description='Build Chromium')
  parser.add_argument('targets', nargs='+', default=[ 'views_examples' ],
                      help='Target build')
  parser.add_argument('-C', dest='out_dir',
                      default=os.path.join(SRC_DIR, 'out/Component'),
                      help='Which config to build')
  args, unknown_args = parser.parse_known_args()

  add_depot_tools_to_path()

  # The python binary used for building is likely the downloaded binary in
  # depot_tools, which does not import modules installed in user's python
  # dir. Export the PYTHONPATH env so modules like pyyaml can be found.
  if current_os() == 'win':
    site_packages = []
    for path in sys.path:
      if path.endswith('site-packages'):
        site_packages.append(path)
    os.environ['PYTHONPATH'] = os.pathsep.join(site_packages)

  ninja_args = [ 'ninja',  '-C', args.out_dir ]
  # Build with many jobs if goma is used.
  if use_goma(args):
    ninja_args += [ '-j', '200' ]

  try:
    subprocess.check_call(ninja_args + unknown_args + args.targets)
  except KeyboardInterrupt:
    sys.exit(1)
  except subprocess.CalledProcessError as e:
    sys.exit(e.returncode)

if __name__ == '__main__':
  main()
