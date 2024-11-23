Onwership Inspector
===================

This project allows you to inspect the ownership of a project using the OWNERSHIP file.

Usage
-----

Full inspection

```bash
> codeowners-inspector .
Unowned: 300
@team-a: 1200
@team-b: 4000
Total: number of files: 5000
```

Inspect a single file or directory

```bash
> codeowners-inspector . --file=README.md
@team-a
```

List all files owned by a single team

```bash
> codeowners-inspector . --team=team-a
./README.md
```
