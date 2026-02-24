# Archive

Completed items from [todo.md](todo.md), preserved for reference.

---

## January 2026

### Completed

- [x] Add pre-commit hooks configuration file *(ruff, mypy, etc)*
- [x] Write development guide *(setup, workflow, etc)*
- [x] Create ADRs *(document architectural decisions)*
- [x] Set up GitHub Actions CI workflow *(testing, linting, etc)*
- [x] Set up Dependabot for automated dependency updates *(learned about rebase-strategy)*
- [x] Create initial changelog file *(Keep a Changelog format)*
- [x] Add GitHub issue templates *(bug report, feature request, etc)*
- [x] Create PR template *(helps standardize contributions)*
- [x] Write initial development documentation *(setup, workflow, etc)*
- [x] Set up Dependabot *(learned about rebase-strategy)*
- [x] Add ADRs *(good for documenting "why")*

## February 2026

### Completed

- [X] Add code coverage reporting to CI
- [X] Set up documentation with MkDocs
- [X] Understand `py.typed` marker for PEP 561
- [X] Learn about `pip-tools` for dependency pinning
- [X] Investigate semantic versioning automation
- [X] Study trusted publishing to PyPI
- [X] Add Docker support for containerized development
- [X] Create VS Code devcontainer configuration
- [X] Add Makefile or taskfile for common commands
- [X] Explore Nox/Tox for multi-environment testing
- [X] Implement Sphinx/MkDocs documentation generation (learn what this even is).
- [X] Explore additional static analysis tools (e.g., Bandit for security)
- [X] Add detailed README.md with badges, usage, etc.   *Although I do have a README.md already, it could be more detailed regarding usage instructions, examples, and badges for build status, coverage, etc.*
- [X] Implement a changelog generation tool (e.g., `towncrier`)
- [X] Add more comprehensive test coverage and edge cases
- [X] Explore using `pip-tools` for managing dependencies with `requirements.txt`
- [X] Learn about semantic versioning and automate version bumps
- [X] Implement Sphinx or MkDocs for documentation generation to create a static site for project docs
- [X] Research best practices for managing `requirements.txt` vs just using `pyproject.toml` dependencies. *From what I've read, `pyproject.toml` is becoming the standard for specifying project metadata and dependencies in Python projects. However, some developers still prefer to use `requirements.txt` for managing dependencies, especially for virtual environments. I should research the pros and cons of each approach and decide which one makes the most sense for this project based on factors like ease of use, compatibility with tools, and team preferences.*
- [X] Learn and build any more scripts and programs within this template repo that may help.
- [X] Add a script that changes the project name, package name, author name, and other relevant info in all necessary files to make it easier to set up a new project from this template. *This could be a Python script that uses regex or string replacement to update the relevant fields in `README.md`, `pyproject.toml`, `LICENSE`, and `SECURITY.md` based on user input. It would save time and reduce the chance of missing any necessary changes when setting up a new project from this template.*
- [X] Add automated releases
- [X] Clarify what workflows this repo has after implementing them in the description of repo and README.md: Core python development workflow with many optional workflows for things like documentation, releases, etc. that are disabled by default to avoid confusion and allow users to enable and adapt them as needed for their own projects. *This would involve updating the README.md and possibly the repository description to clearly outline what workflows are included in the template, which ones are enabled by default, and how users can enable or customize additional workflows based on their needs. This would help users understand the capabilities of the template and how to best utilize it for their projects.*
- [X] create a scripts enable all workflows and another to disable all optional workflows (otherwise explain how to enable each one-by-one). *This could be done with a simple shell script that renames workflow files to enable or disable them. For example, a script to enable all workflows could remove the underscore prefix from all workflow files in the `.github/workflows/` directory, while a script to disable all optional workflows could add an underscore prefix to those files. This would provide a convenient way for users to quickly enable or disable all optional workflows without having to manually rename each file.*
- [X] template auto-fill information for users: integrate cookiecutter + cruft for easier project setup and maintenance. *This would involve creating a `cookiecutter` template based on this repository, which users can use to quickly set up new projects with the same structure and configurations. Additionally, integrating `cruft` would allow users to easily keep their projects up to date with changes made to the template over time. This would streamline the process of starting new projects and maintaining them as the template evolves.*
- [X] Choosing a license for template users: use cookiecutter with license/ directory to allow users to choose a license when setting up a new project. *This would involve creating a `cookiecutter` template that includes a `license/` directory with various license options (e.g., MIT, Apache 2.0, GPL). When users run the `cookiecutter` command to set up a new project, they could be prompted to choose a license from the available options, and the chosen license file would be included in their new project. This would make it easier for users to select and include an appropriate license for their projects.*
- [X] Check CI breadth and add more if needed (e.g., test against more Python versions, add linting or security checks)
- [X] Add more detailed documentation for how to use static analysis tools, including how to set up and customize linters, formatters, and security scanners in CI and locally.
- [X] Add more detailed documentation for how to set up and use documentation generation tools like Sphinx or MkDocs, including how to write docstrings and how to generate and host documentation for the project.
- [X] Add more detailed documentation for how to use GitHub Actions workflows, including how to enable/disable optional workflows, how to customize them for different project needs, and how to troubleshoot common issues with workflows.
- [X] Anymore scripts?
- [X] docs stack: (1) presentation = (Theme: Material for MKDocs), (2) API reference (API reference: mkdocstrings + Python handler), (3) publishing (Markdown power-ups: pymdown-extensions), and optionally (4) versioning (Publishing: GitHub Pages via mkdocs gh-deploy or Read the Docs (RTD)).
- [X] add in docstring style enforcement with a tool like `pydocstyle` to ensure consistent and comprehensive documentation with ruff in pyproject.toml. *This would involve adding `pydocstyle` to the list of dependencies in `pyproject.toml` and configuring it to enforce a specific docstring style (e.g., Google, NumPy, or reStructuredText). This would help ensure that all functions, classes, and modules in the project have consistent and comprehensive docstrings, improving code readability and maintainability.*
- [X] Add in bandit for security linting and checks. *This would involve adding `bandit` to the list of dependencies in `pyproject.toml` and configuring it to run as part of the CI workflow. Bandit would analyze the code for common security issues and vulnerabilities, helping to improve the security posture of projects that use this template.*
- [X] Refactor repo scripts with custom CLI commands
- [X] Add Docker support for containerized development and testing
- [X] Create a VS Code devcontainer configuration for consistent development environments
- [X] Add a Makefile or taskfile for common commands to simplify development workflow
- [X] Explore using Nox or Tox for testing across multiple Python environments
- [X] Read through other popular Python boilerplate repositories to see if there are any common features or best practices I may have missed. *This could include looking at repositories like `cookiecutter`, `python-project-template`, and others to see how they structure their projects, what files they include, and how they handle things like testing, documentation, and CI/CD. It could provide valuable insights and ideas for improving this template.*
- [X] Add in installable CLI command for running tests, linting, or other common tasks. *This could be done using `entry_points` in `pyproject.toml` to create a command-line interface for the project. For example, I could add a command like `myproject test` that runs the test suite, or `myproject lint` that runs the linter. This would make it easier for users to run common tasks without having to remember specific commands or scripts.*
- [X] Task runner: install nox and set up sessions for testing, linting, and other tasks across multiple Python versions. (installed "task" task runner instead) *This would involve adding a `noxfile.py` to the project that defines sessions for running tests, linting, and other common tasks. Each session could be configured to run across multiple Python versions to ensure compatibility. This would provide a convenient way for users to test their code in different environments and maintain code quality with linting.*
- [X] use pre-commit hooks for code formatting, linting, and other checks to maintain code quality. *This would involve setting up a `.pre-commit-config.yaml` file that defines various pre-commit hooks for tasks like code formatting with `black`, linting with `flake8`, and checking for security issues with `bandit`. Users would then need to install the pre-commit hooks in their local environment, which would ensure that these checks are automatically run before each commit, helping to maintain code quality and consistency across the project.*
- [X] add task runner "task"
- [X] When to use `requirements.txt` vs just `pyproject.toml` dependencies?
- [X] Explore `hatch` as alternative to setuptools
- [X] Explore using `hatch` for project management and packaging
- [X] Explore using `hatch` for project management and packaging as an alternative to setuptools
- [X] Where do database files go? (e.g., SQLite files) Should they be in a `data/` directory or something else?
- [X] What is sponsorships and should I allow them for this project? *From what I've read, GitHub Sponsors is a way for open source maintainers to receive financial support from the community. It can be a good way to fund ongoing maintenance and development of the project, but it also requires some effort to set up and manage. I should research how to set it up and decide if it's appropriate for this project based on my goals and expected user base. Also could enable it for example purposes and to learn about the process, even if I don't expect to receive sponsorships right away.*
- [X] Integrate hatch
- [X] use containerfile for consistent development environments and to simplify setup for new contributors. *This would involve creating a `Containerfile` (or `Dockerfile`) that defines a consistent development environment with all necessary dependencies and tools installed. This would allow new contributors to quickly get up and running without having to manually set up their environment, and it would also ensure that everyone is using the same versions of tools and libraries, reducing the chances of environment-related issues.*
- [X] investigate spb clean --todo not working — resolved: the correct command is `spb-clean --todo` (hyphenated entry point), not `spb clean --todo`
- [X] Set up PR workflow
- [X] Verify different PR workflows
- [X] Refactor BUG_BOUNTY.md, SECURITY_no_bounty.md, and SECURITY_with_bounty.md to remove duplication and improve clarity.
