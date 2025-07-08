# archlint Documentation

Python linter focusing on structure. In particular, seeks to enforce:

- a common and predictable structure between source code, tests, and documentation (currently works with `pytest` and `mkdocs+mkdocstrings+mkdocstrings-python`).
- consistent method order (highly configurable)
- import rules (which modules can or cannot import certain modules, internal or external)

`archlint` is fully static, which means it does not require access to the same Python interpreter as the project. This grew out of a collection of development scripts that I had been using across several projects, and I decided to clean them up and package them properly.

`archlint` seeks to fill a few gaps I found, and is not a competitor to any other linter of which I am aware. It is fully tested and its source code conforms to its own standards (i.e. running `archlint` on archlint source code finds no problems). It is not optimized for speed in the way that, for example, `ruff` is; however, on small-to-medium Python projects, its performance feels tolerable.

## Installation

The simplest way to try out `archlint` is via Nix:

```shell
nix run github:yelircaasi/archlint
```

Alternatively, it can be installed with uvx:

```shell
uvx install archlint
archlint
```
