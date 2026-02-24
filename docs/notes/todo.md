# TODO & Ideas

Things to explore, implement, or learn more about.

## To Implement

- [X] Add code coverage reporting to CI
- [X] Set up documentation with MkDocs

## To Learn

- [X] Understand `py.typed` marker for PEP 561
- [X] Learn about `pip-tools` for dependency pinning
- [X] Investigate semantic versioning automation
- [X] Study trusted publishing to PyPI

## Ideas for Later

- [X] Add Docker support for containerized development
- [X] Create VS Code devcontainer configuration
- [X] Add Makefile or taskfile for common commands
- [X] Explore Nox/Tox for multi-environment testing
- [ ] Set up GitHub Codespaces configuration
- [X] Implement Sphinx/MkDocs documentation generation (learn what this even is).
*From what I've read so far this is like a static website generator for documentation, similar to Jekyll but for docs specifically.*
- [ ] Add more ADRs for architectural decisions
- [ ] Add more detailed development workflow docs
- [X] Explore additional static analysis tools (e.g., Bandit for security)
- [X] Add detailed README.md with badges, usage, etc.   *Although I do have a README.md already, it could be more detailed regarding usage instructions, examples, and badges for build status, coverage, etc.*
- [ ] Set up continuous deployment to PyPI on new releases
- [ ] Add support for multiple Python versions in CI
- [X] Implement a changelog generation tool (e.g., `towncrier`)
- [X] Add more comprehensive test coverage and edge cases
- [X] Explore using `pip-tools` for managing dependencies with `requirements.txt`
- [X] Learn about semantic versioning and automate version bumps
- [ ] Study trusted publishing practices for PyPI to ensure secure releases
- [X] Implement Sphinx or MkDocs for documentation generation to create a static site for project docs
- [X] Research best practices for managing `requirements.txt` vs just using `pyproject.toml` dependencies. *From what I've read, `pyproject.toml` is becoming the standard for specifying project metadata and dependencies in Python projects. However, some developers still prefer to use `requirements.txt` for managing dependencies, especially for virtual environments. I should research the pros and cons of each approach and decide which one makes the most sense for this project based on factors like ease of use, compatibility with tools, and team preferences.*
- [ ] Understand all programs within repo
- [X] Learn and build any more scripts and programs within this template repo that may help.
- [X] Add a script that changes the project name, package name, author name, and other relevant info in all necessary files to make it easier to set up a new project from this template. *This could be a Python script that uses regex or string replacement to update the relevant fields in `README.md`, `pyproject.toml`, `LICENSE`, and `SECURITY.md` based on user input. It would save time and reduce the chance of missing any necessary changes when setting up a new project from this template.*
- [X] Add automated releases
- [X] Clarify what workflows this repo has after implementing them in the description of repo and README.md: Core python development workflow with many optional workflows for things like documentation, releases, etc. that are disabled by default to avoid confusion and allow users to enable and adapt them as needed for their own projects. *This would involve updating the README.md and possibly the repository description to clearly outline what workflows are included in the template, which ones are enabled by default, and how users can enable or customize additional workflows based on their needs. This would help users understand the capabilities of the template and how to best utilize it for their projects.*
- [ ] Make other smaller template repos for specific use cases, such as a data science project template, a web application template, etc. *This would involve creating separate repositories that are tailored to specific types of projects, with relevant dependencies, file structures, and example code. For example, a data science project template might include Jupyter notebooks, common data processing libraries, and a structure for organizing datasets and analysis scripts. A web application template might include a basic Flask or Django setup with relevant dependencies and example routes. This would allow users to choose a template that best fits their project needs and get started more quickly.*
- [ ] Make other template repos tailored to "minimal", "library", "cli", etc..
- [ ] Add workflows to enable/disable in USING_THIS_TEMPLATE.md with instructions on how to enable them and what they do. *This would involve updating the `USING_THIS_TEMPLATE.md` file to include a section that lists the optional workflows included in the template, along with instructions on how to enable them (e.g., by renaming workflow files or uncommenting sections in workflow YAML files) and a brief description of what each workflow does. This would help users understand the additional capabilities of the template and how to customize it for their needs.*
- [ ] create a scripts enable all workflows and another to disable all optional workflows (otherwise explain how to enable each one-by-one). *This could be done with a simple shell script that renames workflow files to enable or disable them. For example, a script to enable all workflows could remove the underscore prefix from all workflow files in the `.github/workflows/` directory, while a script to disable all optional workflows could add an underscore prefix to those files. This would provide a convenient way for users to quickly enable or disable all optional workflows without having to manually rename each file.*
- [ ] template auto-fill information for users: integrate cookiecutter + cruft for easier project setup and maintenance. *This would involve creating a `cookiecutter` template based on this repository, which users can use to quickly set up new projects with the same structure and configurations. Additionally, integrating `cruft` would allow users to easily keep their projects up to date with changes made to the template over time. This would streamline the process of starting new projects and maintaining them as the template evolves.*
- [ ] Choosing a license for template users: use cookiecutter with license/ directory to allow users to choose a license when setting up a new project. *This would involve creating a `cookiecutter` template that includes a `license/` directory with various license options (e.g., MIT, Apache 2.0, GPL). When users run the `cookiecutter` command to set up a new project, they could be prompted to choose a license from the available options, and the chosen license file would be included in their new project. This would make it easier for users to select and include an appropriate license for their projects.*
- [ ] Perhaps create a template or project in the future with tools such as copier, cookiecutter, or cruft where users can select from various options (e.g., license type, CI/CD tools, documentation tools) to generate a customized project setup based on their specific needs and preferences. *This would involve creating a more interactive template that allows users to choose from various options when setting up their project. For example, they could select which CI/CD tools they want to include (e.g., GitHub Actions, Travis CI), which documentation tools they prefer (e.g., Sphinx, MkDocs), and which license they want to use. This would provide a more tailored experience for users and allow them to quickly set up a project that fits their requirements without having to manually customize the template after generation.*
- [ ] Populate containerfile with finished product at the end of production pipeline to ensure it always reflects the current state of the project and can be used for consistent development and testing environments. *This would involve updating the `Containerfile` to include all necessary dependencies, tools, and configurations that are required for development and testing. By keeping the `Containerfile` up to date with the finished product, it would ensure that anyone who uses it to create a containerized environment will have everything they need to work on the project without additional setup steps.*
- [ ] Test whole repo against all CI in strict mode. --final stress test--
- [ ] signed tags?
- [ ] add in sql CI?
- [X] Check CI breadth and add more if needed (e.g., test against more Python versions, add linting or security checks)
- [ ] Add more detailed documentation for each workflow and how to customize it for different project needs.
- [ ] Add more detailed documentation for how to set up and use the template for new projects
- [ ] Add more detailed documentation for how to maintain and update projects created from the template, including how to pull in updates from the template itself if using something like `cruft`.
- [ ] Add more detailed documentation for how to use the containerized development environment, including how to build and run the container, and how to use it for development and testing.
- [ ] Add more detailed documentation for how to manage dependencies, including best practices for using `pyproject.toml` vs `requirements.txt`, and how to use tools like `pip-tools` for dependency management.
- [ ] Add more detailed documentation for how to handle versioning and releases, including best practices for semantic versioning and how to automate version bumps and releases to PyPI.
- [ ] Add more detailed documentation for how to write and run tests, including how to use `pytest` markers for categorizing tests (e.g., slow, integration) and how to run specific subsets of tests in CI or locally.
- [ ] Add more detailed documentation for how to use static analysis tools, including how to set up and customize linters, formatters, and security scanners in CI and locally.
- [ ] Add more detailed documentation for how to set up and use documentation generation tools like Sphinx or MkDocs, including how to write docstrings and how to generate and host documentation for the project.
- [ ] Add more detailed documentation for how to use GitHub Actions workflows, including how to enable/disable optional workflows, how to customize them for different project needs, and how to troubleshoot common issues with workflows.
- [ ] Add entire repo each file check
- [ ] Final file check: taskfile.yml
- [ ] Final file check: LICENSE
- [ ] Final file check: README.md
- [ ] Final file check: SECURITY.md
- [ ] Final file check: pyproject.toml
- [ ] Final file check: .github/workflows/ci-gate.yml
- [ ] Final file check: .github/workflows/test.yml
- [ ] Add more detailed design document outlining the architecture and design decisions of the project, including explanations of the file structure, dependency management, testing strategy, CI/CD setup, and any other relevant design choices. This could be added to the `docs/design/` directory as a new markdown file (e.g., `design.md`) that provides an overview of the project's design and architecture for users who want to understand the rationale behind the structure and configurations included in the template.
- [ ] Add resources to learn about dependencies, versioning, packaging, and other relevant topics in the `docs/notes/` directory as a new markdown file (e.g., `resources.md`) that provides links to articles, tutorials, and documentation for users who want to learn more about these topics and how they relate to the project template.
- [X] Anymore scripts?
- [ ] Use and config scripts to liking.
- [ ] Finish a decent amount of todo and finish project for the time being, then add more todos and ideas as they come up in the future. This way I can focus on finishing the project and then iteratively improving it over time rather than getting stuck in an endless loop of planning and adding more todos without making progress on the actual implementation.
- [ ]

## Questions to Answer

- [ ] How to handle private dependencies in pyproject.toml?
- [ ] Best practice for versioning: manual vs automated?
- [ ] When is namespace packaging appropriate?
- [ ] How to manage multiple Python versions in CI?
- [ ] How to handle optional dependencies in pyproject.toml?

## Bookmarks

- [Python Packaging User Guide](https://packaging.python.org/)
- [Scientific Python Development Guide](https://learn.scientific-python.org/development/)
- [Hypermodern Python](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)
