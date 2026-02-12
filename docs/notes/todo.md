# TODO & Ideas

Things to explore, implement, or learn more about.

## To Implement

- [ ] Add code coverage reporting to CI
- [ ] Set up documentation with MkDocs

## To Learn

- [ ] Understand `py.typed` marker for PEP 561
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
- [ ] Research best practices for managing `requirements.txt` vs just using `pyproject.toml` dependencies. *From what I've read, `pyproject.toml` is becoming the standard for specifying project metadata and dependencies in Python projects. However, some developers still prefer to use `requirements.txt` for managing dependencies, especially for virtual environments. I should research the pros and cons of each approach and decide which one makes the most sense for this project based on factors like ease of use, compatibility with tools, and team preferences.*
- [ ] Understand all programs within repo
- [ ] Learn and build any more scripts and programs within this tempalte repo that may help.
- [ ] Add a script that changes the project name, package name, author name, and other relevant info in all necessary files to make it easier to set up a new project from this template. *This could be a Python script that uses regex or string replacement to update the relevant fields in `README.md`, `pyproject.toml`, `LICENSE`, and `SECURITY.md` based on user input. It would save time and reduce the chance of missing any necessary changes when setting up a new project from this template.*
- [ ] Read through other popular Python boilerplate repositories to see if there are any common features or best practices I may have missed. *This could include looking at repositories like `cookiecutter`, `python-project-template`, and others to see how they structure their projects, what files they include, and how they handle things like testing, documentation, and CI/CD. It could provide valuable insights and ideas for improving this template.*   
- [ ] Add in installable CLI command for running tests, linting, or other common tasks. *This could be done using `entry_points` in `pyproject.toml` to create a command-line interface for the project. For example, I could add a command like `myproject test` that runs the test suite, or `myproject lint` that runs the linter. This would make it easier for users to run common tasks without having to remember specific commands or scripts.*
- [ ] Add automated releases
- [ ] Clarify what workflows this repo has after implementing them in the desciption of repo and README.md: Core python development workflow with many optional workflows for things like documentation, releases, etc. that are disabled by default to avoid confusion and allow users to enable and adapt them as needed for their own projects. *This would involve updating the README.md and possibly the repository description to clearly outline what workflows are included in the template, which ones are enabled by default, and how users can enable or customize additional workflows based on their needs. This would help users understand the capabilities of the template and how to best utilize it for their projects.*
- [ ] Make other smaller template repos for specific use cases, such as a data science project template, a web application template, etc. *This would involve creating separate repositories that are tailored to specific types of projects, with relevant dependencies, file structures, and example code. For example, a data science project template might include Jupyter notebooks, common data processing libraries, and a structure for organizing datasets and analysis scripts. A web application template might include a basic Flask or Django setup with relevant dependencies and example routes. This would allow users to choose a template that best fits their project needs and get started more quickly.*
- [ ] Make other template repos tailored to "minimal", "library", "cli", etc..
- [ ] Add workflows to enable/disable in USING_THIS_TEMPLATE.md with instructions on how to enable them and what they do. *This would involve updating the `USING_THIS_TEMPLATE.md` file to include a section that lists the optional workflows included in the template, along with instructions on how to enable them (e.g., by renaming workflow files or uncommenting sections in workflow YAML files) and a brief description of what each workflow does. This would help users understand the additional capabilities of the template and how to customize it for their needs.*
- [ ] create a scripts enable all workflows and another to disable all optional workflows (otherwise explain how to enable each one-by-one). *This could be done with a simple shell script that renames workflow files to enable or disable them. For example, a script to enable all workflows could remove the underscore prefix from all workflow files in the `.github/workflows/` directory, while a script to disable all optional workflows could add an underscore prefix to those files. This would provide a convenient way for users to quickly enable or disable all optional workflows without having to manually rename each file.*
- [ ] docs stack: (1) presentation = (Theme: Material for MKDocs), (2) API reference (API reference: mkdocstrings + Python handler), (3) publishing (Markdown power-ups: pymdown-extensions), and optionally (4) versioning (Publishing: GitHub Pages via mkdocs gh-deploy or Read the Docs (RTD)).
- [ ] Task runner: install nox and set up sessions for testing, linting, and other tasks across multiple Python versions. *This would involve adding a `noxfile.py` to the project that defines sessions for running tests, linting, and other common tasks. Each session could be configured to run across multiple Python versions to ensure compatibility. This would provide a convenient way for users to test their code in different environments and maintain code quality with linting.*
- [ ] template auto-fill information for users: integrate cookiecutter + cruft for easier project setup and maintenance. *This would involve creating a `cookiecutter` template based on this repository, which users can use to quickly set up new projects with the same structure and configurations. Additionally, integrating `cruft` would allow users to easily keep their projects up to date with changes made to the template over time. This would streamline the process of starting new projects and maintaining them as the template evolves.*
- [ ] Choosing a license for template users: use cookiecutter with license/ directory to allow users to choose a license when setting up a new project. *This would involve creating a `cookiecutter` template that includes a `license/` directory with various license options (e.g., MIT, Apache 2.0, GPL). When users run the `cookiecutter` command to set up a new project, they could be prompted to choose a license from the available options, and the chosen license file would be included in their new project. This would make it easier for users to select and include an appropriate license for their projects.*
- [ ] use pre-commit hooks for code formatting, linting, and other checks to maintain code quality. *This would involve setting up a `.pre-commit-config.yaml` file that defines various pre-commit hooks for tasks like code formatting with `black`, linting with `flake8`, and checking for security issues with `bandit`. Users would then need to install the pre-commit hooks in their local environment, which would ensure that these checks are automatically run before each commit, helping to maintain code quality and consistency across the project.*
- [ ] add in docstring style enforcement with a tool like `pydocstyle` to ensure consistent and comprehensive documentation with ruff in pyproject.toml. *This would involve adding `pydocstyle` to the list of dependencies in `pyproject.toml` and configuring it to enforce a specific docstring style (e.g., Google, NumPy, or reStructuredText). This would help ensure that all functions, classes, and modules in the project have consistent and comprehensive docstrings, improving code readability and maintainability.*
  ```toml
  [tool.ruff.lint]
  select = ["D"]

  [tool.ruff.lint.pydocstyle]
  convention = "numpy"
  ```
- [ ] Add in bandit for security linting and checks. *This would involve adding `bandit` to the list of dependencies in `pyproject.toml` and configuring it to run as part of the CI workflow. Bandit would analyze the code for common security issues and vulnerabilities, helping to improve the security posture of projects that use this template.*
- [ ] Perhaps create a template or project in the future with tools such as copier, cookiecutter, or cruft where users can select from various options (e.g., license type, CI/CD tools, documentation tools) to generate a customized project setup based on their specific needs and preferences. *This would involve creating a more interactive template that allows users to choose from various options when setting up their project. For example, they could select which CI/CD tools they want to include (e.g., GitHub Actions, Travis CI), which documentation tools they prefer (e.g., Sphinx, MkDocs), and which license they want to use. This would provide a more tailored experience for users and allow them to quickly set up a project that fits their requirements without having to manually customize the template after generation.*
- [ ] Populate containerfile with finished product at the end of production pipeline to ensure it always reflects the current state of the project and can be used for consistent development and testing environments. *This would involve updating the `Containerfile` to include all necessary dependencies, tools, and configurations that are required for development and testing. By keeping the `Containerfile` up to date with the finished product, it would ensure that anyone who uses it to create a containerized environment will have everything they need to work on the project without additional setup steps.*

## Questions to Answer

- [ ] How to handle private dependencies in pyproject.toml?
- [ ] Best practice for versioning: manual vs automated?
- [ ] When is namespace packaging appropriate?
- [ ] How to manage multiple Python versions in CI?
- [ ] 

## Bookmarks

- [Python Packaging User Guide](https://packaging.python.org/)
- [Scientific Python Development Guide](https://learn.scientific-python.org/development/)
- [Hypermodern Python](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)
