Stakeout
========

This project allows you to inspect the ownership of a project using the OWNERSHIP file.

Usage
-----

Full inspection

```bash
> stakeout .
Unowned: 300
@team-a: 1200
@team-b: 4000
Total: number of files: 5000
```

Inspect a single file or directory

```bash
> stakeout . --file=README.md
@team-a
```

List all files owned by a single team

```bash
> stakeout . --team=team-a
./README.md
```

Develop
-------

```bash
python3 -m venv .env
source ./env/bin/activate
python3 -m pip install -r requirements.txt
```

Distribute
----------

```bash
python3 -m build
python3 -m twine upload --repository stakeout dist/*
```
