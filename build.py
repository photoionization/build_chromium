#!/usr/bin/env python3

import os
import subprocess
import sys

from gn_gen import SRC_DIR, add_depot_tools_to_path

def has_target(args):
  if len(args) < 1:
    return False
  if not args[0].startswith('-'):
    return True
  for i in range(1, len(args)):
    if not args[i].startswith('-') and not args[i - 1].startswith('-'):
      return True
  return False

def use_goma():
  with open(os.path.join(SRC_DIR, 'out/Component/args.gn'), 'r') as f:
    return 'goma.gn' in f.read()

def main(args):
  add_depot_tools_to_path()

  ninja_args = args
  # Set default target if every arg starts with dash.
  if not has_target(args):
    ninja_args += [ 'views_examples' ]
  # Set default out dir unless -C is specified.
  if '-C' not in args:
    ninja_args += [ '-C', os.path.join(SRC_DIR, 'out/Component') ]
  # Build with many jobs if goma is used.
  if use_goma():
    ninja_args += [ '-j', '200' ]

  try:
    subprocess.check_call([ 'ninja' ] + ninja_args)
  except KeyboardInterrupt:
    pass

if __name__ == '__main__':
  main(sys.argv[1:])
