import argparse
import glob
import os
import re
import sys

# Reads the path to inspect along with an optional file to find ownership for or the team for which to file files
def main(root, path: str | None = None, team: str | None = None):
  # If a file is specified, find the owner of the file
  if path:
    print(find_owners(root, path))
  # If a team is specified, find all files owned by the team
  elif team:
    print(find_team_files(root, team))
  # If neither a file nor a team is specified, find all files and their owners
  else:
    try:
      print(find_all_owners(root))
    except Exception as e:
      print(e)

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
    self.paths = []

  def __repr__(self):
    return "Section: %s, Owners: %s, paths: %s" % (self.name, self.owners, self.paths)

  @staticmethod
  def NoneSection():
    return Section("None", [])

class Path(object):
  """A single path that either has own owners or inherits from the parent section"""
  def __init__(self, glob_path: str, owners: list[str]):
    self.glob_path = glob_path
    self.owner = owners

  def __repr__(self):
    return "Path: %s, Owners: %s" % (self.glob_path, self.owner)

def line_to_parts(line: str) -> list[str]:
  return list(filter(lambda x: x, map(lambda x: x.strip(), line.split(' '))))

def read_ownership_file(filepath: str) -> list[Section]:
  # Reads a gitlab ownership file into a structure
  sections: list[Section] = []
  with open(filepath, 'r') as f:
    for line_number, line_raw in enumerate(f):
      line = line_raw.strip()
      # This is a comment line
      if line.startswith('#') or len(line) == 0:
        continue

      # There are two ways to indicate a section: either with a [section_name] or ^[section_name].
      #
      # The section name can also be followed by a number indicating the minimum number of reviewers and
      # a list of owners.

      if line.startswith('[') or line.startswith('^['):
        result = re.search(r'^(\^)?\[([^\]]+)\](\[\d\])?(.*)$', line)
        if result is None:
          raise ValueError('Invalid section name on line %d: %s' % (line_number, line_raw))

        sections.append(Section(
          name=result.group(2),
          owners=line_to_parts(result.group(4)),
        ))

      if len(sections) == 0:
        sections.append(Section.NoneSection())

      # This is f path line
      parts = list(map(lambda x: x.strip(), line.split(' ')))
      sections[-1].paths.append(Path(parts[0], parts[1:]))

      # if line.startswith('*'):
      #   sections.append(current_section)
      #   current_section = Section(line[1:].strip(), [])
      # else:
      #   parts = line.split()
      #   if len(parts) == 0:
      #     continue
      #   current_section.owners.append(parts[0])
      #   for path in parts[1:]:
      #     current_section.paths.append(Path(path, parts[0]))
  return sections

def find_owners(path, file):
    # Find the owner of the file
    return 'owners'

def find_team_files(path, team):
    # Find all files owned by the team
    return 'files'

def find_all_owners(path):
    # Find all files and their owners
    return read_ownership_file(find_ownership_file(path))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
  prog='python3 ownership-inspector.py',
  usage='%(prog)s [options]',
  description='List ownership for the project, a single team, or a single file')

  parser.add_argument('root')
  parser.add_argument('--path', type=str, help='The path to inspect')
  parser.add_argument('--team', type=str, help='The team for which to list files')
  args = parser.parse_args(sys.argv[1:])

  main(args.root, args.path, args.team)
