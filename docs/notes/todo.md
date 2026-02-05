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
- [ ] Explore using `hatch` for project management and packaging as an alternative to setuptools
- [ ] Where do database files go? (e.g., SQLite files) Should they be in a `data/` directory or something else?
- [ ] What is sponsorships and should I allow them for this project? *From what I've read, GitHub Sponsors is a way for open source maintainers to receive financial support from the community. It can be a good way to fund ongoing maintenance and development of the project, but it also requires some effort to set up and manage. I should research how to set it up and decide if it's appropriate for this project based on my goals and expected user base. Also could enable it for example purposes and to learn about the process, even if I don't expect to receive sponsorships right away.*
- [ ] Research best practices for managing `requirements.txt` vs just using `pyproject.toml` dependencies. *From what I've read, `pyproject.toml` is becoming the standard for specifying project metadata and dependencies in Python projects. However, some developers still prefer to use `requirements.txt` for managing dependencies, especially for virtual environments. I should research the pros and cons of each approach and decide which one makes the most sense for this project based on factors like ease of use, compatibility with tools, and team preferences.*
- [ ] Understand all programs within repo
- [ ] Learn and build any more scripts and programs within this tempalte repo that may help.
- [ ] Add a script that changes the project name, package name, author name, and other relevant info in all necessary files to make it easier to set up a new project from this template. *This could be a Python script that uses regex or string replacement to update the relevant fields in `README.md`, `pyproject.toml`, `LICENSE`, and `SECURITY.md` based on user input. It would save time and reduce the chance of missing any necessary changes when setting up a new project from this template.*
- [ ] Read through other popular Python boilerplate repositories to see if there are any common features or best practices I may have missed. *This could include looking at repositories like `cookiecutter`, `python-project-template`, and others to see how they structure their projects, what files they include, and how they handle things like testing, documentation, and CI/CD. It could provide valuable insights and ideas for improving this template.*   
- [ ] Add in installable CLI command for running tests, linting, or other common tasks. *This could be done using `entry_points` in `pyproject.toml` to create a command-line interface for the project. For example, I could add a command like `myproject test` that runs the test suite, or `myproject lint` that runs the linter. This would make it easier for users to run common tasks without having to remember specific commands or scripts.*
- [ ]

## Questions to Answer

- When to use `requirements.txt` vs just `pyproject.toml` dependencies?
- How to handle private dependencies in pyproject.toml?
- Best practice for versioning: manual vs automated?
- When is namespace packaging appropriate?

## Bookmarks

- [Python Packaging User Guide](https://packaging.python.org/)
- [Scientific Python Development Guide](https://learn.scientific-python.org/development/)
- [Hypermodern Python](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)
