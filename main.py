import argparse
import fnmatch
import glob
import os
import pathlib
import re
import sys
from typing import Iterator

# Reads the path to inspect along with an optional file to find ownership for or the team for which to file files
def main(root_raw, path: str | None = None, owner: str | None = None):
  root = os.path.abspath(root_raw).rstrip('/')

  # If a file is specified, find the owner of the file
  if path:
    all_owners = set()
    all_paths = find_all_owners(root)
    clean_path = os.path.join('/', path.lstrip('/'))
    for a_path in all_paths:
      if fnmatch.fnmatch(clean_path, a_path.glob_path):
        all_owners.update(a_path.owners)
    if len(all_owners) > 0:
      print("\n".join(all_owners))
  # If a team is specified, find all files owned by the team
  elif owner:
    all_paths = find_all_owners(root)
    all_paths_for_owner = [path for path in all_paths if owner in path.owners]
    for file in list_all_files(root):
      for path_for_owner in all_paths_for_owner:
        if fnmatch.fnmatch(file, path_for_owner.glob_path):
          print(file)
  # If neither a file nor a team is specified, find all files and their owners
  else:
    try:
      total = 0
      unowned = 0
      ownership_count: dict[str, int] = {}
      all_paths = find_all_owners(root)
      for file in list_all_files(root):
        total += 1
        found = False
        for a_path in all_paths:
          if len(a_path.owners) > 0 and fnmatch.fnmatch(file, a_path.glob_path):
            found = True
            for an_owner in a_path.owners:
              if an_owner not in ownership_count:
                ownership_count[an_owner] = 0
              ownership_count[an_owner] += 1
        if not found:
          unowned += 1
      print("Total: %d\nUnowned: %d\n%s" % (total, unowned, '\n'.join(["%s: %d" % (k, v) for k, v in ownership_count.items()])))
    except Exception as e:
      print(e)

def list_all_files(path, original_root = None, ignored: list[str] = []) -> Iterator[str]:
  """Returns a list of all files in the path excluding the path name"""
  yield from __iterate_over_files(path, path, [])

def __iterate_over_files(path, original_root, ignored: list[str] = []) -> Iterator[str]:
  """Returns a list of all files in the path excluding the path name"""
  files = os.listdir(path)
  for f in files:
    full_file_path = os.path.join(path, f)
    if os.path.isdir(full_file_path):
      yield from __iterate_over_files(full_file_path, original_root, ignored)
    else:
      relative_file_path = full_file_path[len(original_root):]
      for ignored_glog in ignored:
        if fnmatch.fnmatch(relative_file_path, ignored_glog):
          break
      else:
        yield relative_file_path
        continue
      break

def find_ownership_file(root: str) -> str:
    # Read the ownership file
    paths = [
      'CODEOWNERS',
      '.git/CODEOWNERS'
    ]
    for path in paths:
      full_path = os.path.join(root, path)
      if os.path.exists(full_path):
          return full_path
    raise FileNotFoundError('No CODEOWNERS file found')

class Section(object):
  """A section contains a list of owners and a list of expressions to match files"""
  def __init__(self, name, owners):
    self.name = name
    self.owners = owners

class Path(object):
  """A single path that either has own owners or inherits from the parent section"""
  def __init__(self, glob_path: str, owners: list[str], section: Section | None = None):
    self.glob_path = glob_path
    self.section = section

    if len(owners) > 0:
      self.owners = owners
    elif section is not None:
      self.owners = section.owners

  def __repr__(self):
    section_name = self.section.name if self.section is not None else 'None'
    return "Path: %s - Owners: %s - Section: %s" % (self.glob_path, self.owners, section_name)

def line_to_parts(line: str) -> list[str]:
  return list(filter(lambda x: x, map(lambda x: x.strip(), line.split(' '))))

def read_ownership_file(filepath: str) -> list[Path]:
  # Reads a gitlab ownership file into a structure
  paths: list[Path] = []
  current_section = None

  with open(filepath, 'r') as f:
    for line_number, line_raw in enumerate(f):
      line = line_raw.strip()

      # Removes comments
      line = line.split('#')[0].strip()

      # This is a comment line
      if len(line) == 0:
        continue

      # There are two ways to indicate a section: either with a [section_name] or ^[section_name].
      #
      # The section name can also be followed by a number indicating the minimum number of reviewers and
      # a list of owners.

      if line.startswith('[') or line.startswith('^['):
        result = re.search(r'^(\^)?\[([^\]]+)\](\[\d\])?(.*)$', line)
        if result is None:
          raise ValueError('Invalid section name on line %d: %s' % (line_number, line_raw))

        current_section = Section(
          name=result.group(2),
          owners=line_to_parts(result.group(4)),
        )
        continue

      # This is file path line
      parts = list(map(lambda x: x.strip(), line.split(' ')))
      file_glob = parts[0]
      if not file_glob.startswith(os.sep):
        # Fixes the path to match any file regardless of the directory, if it
        # doesn't start with a slash
        file_glob = '**/%s' % file_glob
      paths.append(Path(file_glob, parts[1:], section=current_section))
  return paths

def find_all_owners(path):
    # Find all files and their owners
    return read_ownership_file(find_ownership_file(path))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
  prog='python3 main.py',
  usage='%(prog)s [options]',
  description='List ownership for the project, a single owner, or a single file')

  parser.add_argument('root')
  parser.add_argument('--path', type=str, help='The path to inspect')
  parser.add_argument('--owner', type=str, help='The owner for which to list files')
  args = parser.parse_args(sys.argv[1:])

  main(args.root, args.path, args.owner)
