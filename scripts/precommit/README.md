# Pre-commit Scripts

Custom [pre-commit](https://pre-commit.com/) hooks used by this project.

These scripts are called from `.pre-commit-config.yaml` under the `repo: local` section.

## Contents

| Script                                   | Hook ID        | Description                                       |
| ---------------------------------------- | -------------- | ------------------------------------------------- |
| [check_nul_bytes.py](check_nul_bytes.py) | `no-nul-bytes` | Fail if any staged file contains NUL (0x00) bytes |
