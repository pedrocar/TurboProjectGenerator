import os
import subprocess
import pty
import sys
import select
import json

# Define the checkpoint file
CHECKPOINT_FILE = "script_status.txt"

# Function to read the current step from the checkpoint file
def read_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as file:
            return int(file.read().strip())
    return 0

# Function to update the checkpoint file
def update_checkpoint(step):
    with open(CHECKPOINT_FILE, "w") as file:
        file.write(str(step))

# General function to execute a command
def execute_command(command, work_dir=None):
    if command[0] == "cd":
        try:
            os.chdir(command[1])
            print(f"Changed directory to {command[1]}")
        except Exception as e:
            print(f"Failed to change directory: {e}")
            return False
    else:
        try:
            if work_dir and not os.path.exists(work_dir):
                os.makedirs(work_dir)
                print(f"Created directory {work_dir}")

            master, slave = pty.openpty()
            process = subprocess.Popen(command, stdin=slave, stdout=slave, stderr=slave, cwd=work_dir, text=True)
            os.close(slave)

            stdout_output = []
            stderr_output = []

            while True:
                r, _, _ = select.select([master], [], [], 0.1)
                if r:
                    try:
                        output = os.read(master, 1024).decode('utf-8')
                    except OSError as e:
                        if e.errno == 5:
                            break  # Ignore I/O error caused by the subprocess closing the file descriptor
                        raise

                    if output:
                        sys.stdout.write(output)
                        sys.stdout.flush()
                        stdout_output.append(output)
                        if process.poll() is None and output.strip().endswith('?'):
                            user_input = input()
                            os.write(master, f"{user_input}\n".encode('utf-8'))
                if process.poll() is not None:
                    break

            process.wait()  # Ensure the process has finished
            os.close(master)

            combined_output = ''.join(stdout_output)
            if "error" in combined_output.lower():
                print(f"Command failed with error: {combined_output}")
                return False

            if process.returncode != 0:
                print(f"Command failed with return code {process.returncode}")
                return False

        except Exception as e:
            print(f"Command execution failed: {e}")
            return False
    return True

# General function to execute a step
def execute_step(step_number, commands, work_dir=None):
    current_step = read_checkpoint()
    if current_step >= step_number:
        print(f"Step {step_number} already completed. Skipping...")
        return True
    print(f"Executing Step {step_number}...")
    for command in commands:
        if not execute_command(command, work_dir=work_dir):
            print(f"Step {step_number} failed.")
            return False
    update_checkpoint(step_number)
    return True

def main():
    # Path to the setup_config.json file
    config_path = 'setup_config.json'
    
    # Open and read the setup_config.json file
    with open(config_path, 'r') as config_file:
        config_data = json.load(config_file)
    
    # Set GitHub token as an environment variable for authentication
    os.environ['GITHUB_TOKEN'] = config_data['github']['token']
    
    steps = [
        (1, [
            ["cd", "projects"],
            ["mkdir", "-p", config_data['common']['folder_name']],
            ["cd", config_data['common']['folder_name']],
            [
                "cookiecutter", 
                "https://github.com/cookiecutter/cookiecutter-django",
                "--no-input",
                f"project_name={config_data['backend']['project_name']}",
                f"project_slug={config_data['backend']['project_slug']}",
                f"description={config_data['backend']['description']}",
                f"author_name={config_data['backend']['author_name']}",
                f"domain_name={config_data['backend']['domain_name']}",
                f"email={config_data['backend']['email']}",
                f"version={config_data['backend']['version']}",
                f"timezone={config_data['backend']['timezone']}",
                f"use_whitenoise={config_data['backend']['use_whitenoise']}",
                f"use_celery={config_data['backend']['use_celery']}",
                f"use_mailhog={config_data['backend']['use_mailhog']}",
                f"use_sentry={config_data['backend']['use_sentry']}",
                f"use_docker={config_data['backend']['use_docker']}",
                f"use_heroku={config_data['backend']['use_heroku']}",
                f"ci_tool={config_data['backend']['ci_tool']}",
                f"keep_local_envs_in_vcs={config_data['backend']['keep_local_envs_in_vcs']}",
                f"debug={config_data['backend']['debug']}",
                f"custom_bootstrap_compilation={config_data['backend']['custom_bootstrap_compilation']}",
                f"use_compressor={config_data['backend']['use_compressor']}",
                f"postgresql_version={config_data['backend']['postgresql_version']}",
                f"js_task_runner={config_data['backend']['js_task_runner']}",
                f"cloud_provider={config_data['backend']['cloud_provider']}",
                f"mail_service={config_data['backend']['mail_service']}",
                f"use_async={config_data['backend']['use_async']}",
                f"windows={config_data['backend']['windows']}",
                f"use_drf={config_data['backend']['use_drf']}",
                f"custom_drf_model_view_set={config_data['backend']['custom_drf_model_view_set']}",
                f"license={config_data['backend']['license']}"
            ],
            ["cd", ".."],
            ["cd", ".."]
        ]),
        (2, [
            #TODO: build and test backend project
        ]),
        (3, [
            ["cd", "projects"],
            ["cd", config_data['common']['folder_name']],
            [
                "npx",
                "create-next-app@latest",
                config_data['frontend']['project_slug'],
                "--ts" if config_data['frontend']['use_typescript'] == "y" else "--ts",
                "--eslint" if config_data['frontend']['use_eslint'] == "y" else "--no-eslint",
                "--tailwind" if config_data['frontend']['use_tailwind'] == "y" else "--no-tailwind",
                "--src-dir" if config_data['frontend']['use_src_dir'] == "y" else "--no-src-dir",
                "--app" if config_data['frontend']['use_app_router'] == "y" else "--no-app",
                "--import-alias" if config_data['frontend']['use_custom_import_alias'] == "y" else "--no-import-alias",
                config_data['frontend']['custom_import_alias'] if config_data['frontend']['custom_import_alias'] != "None" else "",
            ],
            ["cd", ".."],
            ["cd", ".."]
        ]),
        (4, [
            #TODO: build and test frontend project
        ]),
        (5, [
            ["cd", "projects"],
            ["cd", config_data['common']['folder_name']],
            ["rm", "-rf", ".git"],
            ["git", "init"],
            ["git", "add", "."],
            ["git", "commit", "-m", "Initial commit"],
            ["gh", "repo", "create", f"{config_data['github']['username']}/{config_data['github']['repository_name']}", "--public", "--source=.", "--remote=origin"],
            ["git", "push", "-u", "origin", "master"],
            ["cd", ".."],
            ["cd", ".."]
        ]),
        (6, [
            # ["echo", "Terraform config applied"]
        ])
    ]

    for step in steps:
        step_number, commands = step[0], step[1]
        work_dir = step[2] if len(step) > 2 else None
        if not execute_step(step_number, commands, work_dir=work_dir):
            break

if __name__ == "__main__":
    main()
