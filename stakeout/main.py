import argparse
import sys

from stakeout.stakeout import main

def run():
  '''Runs the program'''
  parser = argparse.ArgumentParser(
  prog='stakeout',
  usage='%(prog)s [options]',
  description='List ownership for the project, a single owner, or a single file')

  parser.add_argument('root')
  parser.add_argument('--path', type=str, help='The path to inspect')
  parser.add_argument('--owner', type=str, help='The owner for which to list files')
  args = parser.parse_args(sys.argv[1:])

  main(args.root, args.path, args.owner)

if __name__ == '__main__':
  run()
