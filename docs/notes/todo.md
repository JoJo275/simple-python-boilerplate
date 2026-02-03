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
- [ ] Create example scripts or notebooks demonstrating package usage
- [ ] Set up continuous deployment to PyPI on new releases
- [ ] Refactor repo scripts with custom CLI commands
- [ ] Explore using `hatch` for project management and packaging
- [ ] Add support for multiple Python versions in CI
- [ ] Implement a changelog generation tool (e.g., `towncrier`)
- [ ] Add more comprehensive test coverage and edge cases
- [ ] Explore using `pip-tools` for managing dependencies with `requirements.txt`
- [ ] Learn about semantic versioning and automate version bumps
- [ ] Study trusted publishing practices for PyPI to ensure secure releases
- [ ] Add Docker support for containerized development and testing
- [ ] Create a VS Code devcontainer configuration for consistent development environments
- [ ] Add a Makefile or taskfile for common commands to simplify development workflow
- [ ] Explore using Nox or Tox for testing across multiple Python environments
- [ ] Set up GitHub Codespaces configuration for cloud-based development environments
- [ ] Implement Sphinx or MkDocs for documentation generation to create a static site for project docs
- [ ] Set up PR workflow
- [ ] Verify different PR workflows
- [ ] Explore using `hatch` for project management and packaging as an alternative to setuptools
- [ ] Where do database files go? (e.g., SQLite files) Should they be in a `data/` directory or something else?
- [ ] What is sponsorships and should I allow them for this project? *From what I've read, GitHub Sponsors is a way for open source maintainers to receive financial support from the community. It can be a good way to fund ongoing maintenance and development of the project, but it also requires some effort to set up and manage. I should research how to set it up and decide if it's appropriate for this project based on my goals and expected user base. Also could enable it for example purposes and to learn about the process, even if I don't expect to receive sponsorships right away.*

## Questions to Answer

- When to use `requirements.txt` vs just `pyproject.toml` dependencies?
- How to handle private dependencies in pyproject.toml?
- Best practice for versioning: manual vs automated?
- When is namespace packaging appropriate?

## Bookmarks

- [Python Packaging User Guide](https://packaging.python.org/)
- [Scientific Python Development Guide](https://learn.scientific-python.org/development/)
- [Hypermodern Python](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)
