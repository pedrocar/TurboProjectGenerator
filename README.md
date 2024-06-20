# Turbo Project Generator

This project automates the creation of the codebase for backend and frontend subprojects and integrates them with GitHub and Digital Ocean.

## Purpose

The purpose of this project is to streamline the setup and integration of backend and frontend subprojects by automating the process and reducing manual intervention.

## Prerequisites

Ensure the following are installed locally before running this project:

1. **Git**: Version control system
2. **Python**: Programming language
3. **npx**: Node Package Runner
4. **Docker**: Containerization platform
5. **Docker Compose**: Tool for defining and running multi-container Docker applications
6. **Cookiecutter**: A command-line utility that creates projects from project templates
7. **Gh**: Github client

## Setup Instructions

Follow these steps to set up and run the project:

1. **Configure the Project:**
   - Edit the `setup_config.json` file to match the configuration of the project you want to create.

2. **Initialize the Script Status:**
   - Delete the `script_status` file or update it with a value of `0`.

3. **Run the Setup Script:**
   - Execute the following command:
     ```bash
     python3 setup_project.py
     ```

## Contribution

We welcome contributions to improve and extend this project. Please fork the repository and submit pull requests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
