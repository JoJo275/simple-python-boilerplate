# TODO & Ideas

Things to explore, implement, or learn more about.

## To Implement

- [ ] Add code coverage reporting to CI
- [ ] Set up documentation with MkDocs

## To Learn

- [ ] Understand `py.typed` marker for PEP 561
- [ ] Explore `hatch` as alternative to setuptools
- [ ] Learn about `pip-tools` for dependency pinning
- [ ] Investigate semantic versioning automation
- [ ] Study trusted publishing to PyPI

## Ideas for Later

- [ ] Add Docker support for containerized development
- [ ] Create VS Code devcontainer configuration
- [ ] Add Makefile or taskfile for common commands
- [ ] Explore Nox/Tox for multi-environment testing
- [ ] Set up GitHub Codespaces configuration
- [ ] Implement Sphinx/MkDocs documentation generation (learn what this even is).  
*From what I've read so far this is like a static website generator for documentation, similar to Jekyll but for docs specifically.*
- [ ] Add more ADRs for architectural decisions
- [ ] Add more detailed development workflow docs
- [ ] Explore additional static analysis tools (e.g., Bandit for security)
- [ ] Add detailed README.md with badges, usage, etc.   *Although I do have a README.md already, it could be more detailed regarding usage instructions, examples, and badges for build status, coverage, etc.*

## Questions to Answer

- When to use `requirements.txt` vs just `pyproject.toml` dependencies?
- How to handle private dependencies in pyproject.toml?
- Best practice for versioning: manual vs automated?
- When is namespace packaging appropriate?

## Bookmarks

- [Python Packaging User Guide](https://packaging.python.org/)
- [Scientific Python Development Guide](https://learn.scientific-python.org/development/)
- [Hypermodern Python](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)
