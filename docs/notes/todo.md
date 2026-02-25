# TODO & Ideas

Things to explore, implement, or learn more about.

## To Implement

## To Learn

## Ideas for Later

- [ ] Set up GitHub Codespaces configuration
*From what I've read so far this is like a static website generator for documentation, similar to Jekyll but for docs specifically.*
- [ ] Add more ADRs for architectural decisions
- [ ] Add more detailed development workflow docs
- [ ] Set up continuous deployment to PyPI on new releases
- [ ] Add support for multiple Python versions in CI
- [X] Study trusted publishing practices for PyPI to ensure secure releases
- [ ] Understand all programs within repo
- [ ] Make other smaller template repos for specific use cases, such as a data science project template, a web application template, etc. *This would involve creating separate repositories that are tailored to specific types of projects, with relevant dependencies, file structures, and example code. For example, a data science project template might include Jupyter notebooks, common data processing libraries, and a structure for organizing datasets and analysis scripts. A web application template might include a basic Flask or Django setup with relevant dependencies and example routes. This would allow users to choose a template that best fits their project needs and get started more quickly.*
- [ ] Make other template repos tailored to "minimal", "library", "cli", etc..
- [ ] Add workflows to enable/disable in USING_THIS_TEMPLATE.md with instructions on how to enable them and what they do. *This would involve updating the `USING_THIS_TEMPLATE.md` file to include a section that lists the optional workflows included in the template, along with instructions on how to enable them (e.g., by renaming workflow files or uncommenting sections in workflow YAML files) and a brief description of what each workflow does. This would help users understand the additional capabilities of the template and how to customize it for their needs.*
- [ ] Perhaps create a template or project in the future with tools such as copier, cookiecutter, or cruft where users can select from various options (e.g., license type, CI/CD tools, documentation tools) to generate a customized project setup based on their specific needs and preferences. *This would involve creating a more interactive template that allows users to choose from various options when setting up their project. For example, they could select which CI/CD tools they want to include (e.g., GitHub Actions, Travis CI), which documentation tools they prefer (e.g., Sphinx, MkDocs), and which license they want to use. This would provide a more tailored experience for users and allow them to quickly set up a project that fits their requirements without having to manually customize the template after generation.*
- [ ] Populate containerfile with finished product at the end of production pipeline to ensure it always reflects the current state of the project and can be used for consistent development and testing environments. *This would involve updating the `Containerfile` to include all necessary dependencies, tools, and configurations that are required for development and testing. By keeping the `Containerfile` up to date with the finished product, it would ensure that anyone who uses it to create a containerized environment will have everything they need to work on the project without additional setup steps.*
- [ ] Test whole repo against all CI in strict mode. --final stress test--
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
- [ ] Use and config scripts to liking.
- [ ] Finish a decent amount of todo and finish project for the time being, then add more todos and ideas as they come up in the future. This way I can focus on finishing the project and then iteratively improving it over time rather than getting stuck in an endless loop of planning and adding more todos without making progress on the actual implementation.
- [ ] Make sure each docs has the proper information and relevant links to resources and other docs that may help.
- [ ] Make sure relevant commands are organized for end-users.
- [ ]

## Questions to Answer

- [X] How to handle private dependencies in pyproject.toml?
- [X] Best practice for versioning: manual vs automated?
- [X] When is namespace packaging appropriate?
- [X] How to manage multiple Python versions in CI?
- [ ] How to handle optional dependencies in pyproject.toml?

## Bookmarks

- [Python Packaging User Guide](https://packaging.python.org/)
- [Scientific Python Development Guide](https://learn.scientific-python.org/development/)
- [Hypermodern Python](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)
