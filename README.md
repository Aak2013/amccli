# AMC CLI

A small terminal-first CLI for importing AMC-style math questions and practicing them locally.

## Install

```bash
pip install -e .
```

## Commands

```bash
amc --help
amc init
amc import data/questions_v1.jsonl --dedupe
amc list --contest AMC12 --year 2023
amc show 1 --with-answer --with-solution
amc practice --count 5
amc stats
amc recommend --count 5
```

## Notes

- The tool stores its local database under `~/.amc-cli/amc.db` by default.
- Complex formulas are kept in LaTeX form and can be simplified with `--plain`.
- This is a local-only MVP and intentionally avoids multi-user/cloud features.
