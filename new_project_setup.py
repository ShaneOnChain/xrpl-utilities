import os
import subprocess
import shutil

# Configuration for the project setup directory and some constants
BASE_DIR = "C:\\Projects"
GITIGNORE_TEMPLATE = ".gitignore_template"
GITIGNORE_CONTENT = """# Python related
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

env/
.venv/
venv/
ENV/
env.bak/
venv.bak/

# VSCode related
.vscode/
*.code-workspace

# Others
*.log
*.sqlite3
dist/
build/
*.egg-info/
"""


# Create the project folder
def create_project_directory(project_name):
    project_path = os.path.join(BASE_DIR, project_name)
    if not os.path.exists(project_path):
        os.makedirs(project_path)
    return project_path


# Set up the virtual environment in the specified folder
def setup_venv(project_path):
    venv_path = os.path.join(project_path, "venv")
    subprocess.run(["python", "-m", "venv", venv_path], check=True)
    print(f"Virtual environment created at: {venv_path}")
    return venv_path


# Create a .gitignore file in the specified folder
def create_gitignore(project_path):
    gitignore_path = os.path.join(project_path, ".gitignore")
    with open(gitignore_path, "w") as gitignore_file:
        gitignore_file.write(GITIGNORE_CONTENT)
    print(".gitignore created with common Python and VSCode ignore rules.")


# Install requirements if a requirements file is present
def install_requirements(project_path, venv_path):
    requirements_file = os.path.join(project_path, "requirements.txt")
    pip_path = os.path.join(venv_path, "Scripts", "pip")
    if os.path.exists(requirements_file):
        subprocess.run([pip_path, "install", "-r", requirements_file], check=True)
        print(f"Requirements installed from {requirements_file}")


# Optionally install XRPL-Py, Flask, or both
def optional_installs(venv_path, project_path):
    pip_path = os.path.join(venv_path, "Scripts", "pip")
    options = {
        "1": "Flask",
        "2": "xrpl-py",
        "3": "Both Flask and XRPL-Py",
    }
    print("Optional installations:")
    print("1 - Flask")
    print("2 - XRPL-Py")
    print("3 - Both Flask and XRPL-Py")
    choice = input("Enter the option to install (or press Enter to skip): ")
    if choice in options:
        if choice == "3":
            libraries = ["Flask", "xrpl-py"]
        else:
            libraries = [options[choice]]
        for library in libraries:
            subprocess.run([pip_path, "install", library], check=True)
            print(f"{library} has been installed successfully.")

        # Create basic Flask boilerplate if Flask is installed
        if "Flask" in libraries:
            create_flask_boilerplate(project_path)


# Create a basic beginner Flask boilerplate file along with supporting directories
def create_flask_boilerplate(project_path):
    app_file_path = os.path.join(project_path, "app.py")
    flask_boilerplate = """from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(debug=True)
"""
    with open(app_file_path, "w") as app_file:
        app_file.write(flask_boilerplate)
    print("Basic Flask boilerplate created as app.py.")

    # Create Flask supporting directories
    templates_path = os.path.join(project_path, "templates")
    static_path = os.path.join(project_path, "static")
    os.makedirs(templates_path, exist_ok=True)
    os.makedirs(static_path, exist_ok=True)
    
    # Create static subdirectories
    documents_path = os.path.join(static_path, "documents")
    images_path = os.path.join(static_path, "images")
    styles_path = os.path.join(static_path, "styles")
    os.makedirs(documents_path, exist_ok=True)
    os.makedirs(images_path, exist_ok=True)
    os.makedirs(styles_path, exist_ok=True)
    print("Flask supporting directories 'templates' and 'static' with subdirectories 'documents', 'images', and 'styles' created.")


# Dump the requirements to a requirements.txt file
def dump_requirements(venv_path, project_path):
    pip_path = os.path.join(venv_path, "Scripts", "pip")
    requirements_path = os.path.join(project_path, "requirements.txt")
    with open(requirements_path, "w") as requirements_file:
        subprocess.run([pip_path, "freeze"], stdout=requirements_file, check=True)
    print(f"Requirements dumped to {requirements_path}")


# Main script
if __name__ == "__main__":
    project_name = input("Enter the project name: ")
    if not project_name:
        print("Project name cannot be empty.")
    else:
        project_path = create_project_directory(project_name)
        setup_venv_path = setup_venv(project_path)
        create_gitignore(project_path)
        install_requirements(project_path, setup_venv_path)
        optional_installs(setup_venv_path, project_path)
        dump_requirements(setup_venv_path, project_path)
        print(f"Project setup complete for: {project_name} in {project_path}")
