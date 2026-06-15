import os
import subprocess
import json
import sys

def run_command(command, cwd=None):
    """Run a command with proper Windows path handling."""
    try:
        # Use npm.cmd instead of npm on Windows
        if os.name == 'nt':  # Windows
            if command[0] == 'npm':
                command[0] = 'npm.cmd'
            elif command[0] == 'npx':
                command[0] = 'npx.cmd'
        
        print(f"Running command: {' '.join(command)}")
        subprocess.run(command, cwd=cwd, check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(f"Error details: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

def create_project(name):
    """Create and set up a React frontend with Node.js backend project."""
    try:
        base_dir = os.path.join(os.getcwd(), name)
        
        # Create project directories
        os.makedirs(os.path.join(base_dir, 'frontend'), exist_ok=True)
        os.makedirs(os.path.join(base_dir, 'backend'), exist_ok=True)
        
        print("Created project directories")
        
        # Set up frontend (React)
        frontend_dir = os.path.join(base_dir, 'frontend')
        print("\nSetting up React frontend...")
        if not run_command(['npx', 'create-react-app', '.'], frontend_dir):
            print("Failed to create React app")
            return
        
        # Set up backend (Node/Express)
        print("\nSetting up Node.js backend...")
        backend_dir = os.path.join(base_dir, 'backend')
        
        # Create package.json for backend
        backend_package = {
            "name": f"{name}-backend",
            "version": "1.0.0",
            "main": "server.js",
            "scripts": {
                "start": "node server.js",
                "dev": "nodemon server.js"
            },
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5"
            },
            "devDependencies": {
                "nodemon": "^3.0.2"
            }
        }
        
        with open(os.path.join(backend_dir, 'package.json'), 'w') as f:
            json.dump(backend_package, f, indent=2)
        print("Created backend package.json")
        
        # Create basic Express server
        server_code = """const express = require('express');
const cors = require('cors');
const app = express();
const port = 5000;

app.use(cors());
app.use(express.json());

app.get('/api/test', (req, res) => {
    res.json({ message: 'Backend is working!' });
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});"""
        
        with open(os.path.join(backend_dir, 'server.js'), 'w') as f:
            f.write(server_code)
        print("Created server.js")
        
        # Install backend dependencies
        print("\nInstalling backend dependencies...")
        if not run_command(['npm', 'install'], backend_dir):
            print("Failed to install backend dependencies")
            return
        
        print(f"""
Project created successfully!

To start the frontend:
cd {name}/frontend
npm start

To start the backend:
cd {name}/backend
npm run dev

Frontend will run on: http://localhost:3000
Backend will run on: http://localhost:5000
""")

    except Exception as e:
        print(f"Error creating project: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure Node.js and npm are installed")
        print("2. Try running 'node --version' and 'npm --version' in a new terminal")
        print("3. Make sure you have write permissions in the current directory")

if __name__ == "__main__":
    # Check if Node.js is installed
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
    except FileNotFoundError:
        print("Error: Node.js is not installed. Please install Node.js first.")
        sys.exit(1)

    project_name = input("Enter project name: ")
    if not project_name:
        print("Project name cannot be empty")
    else:
        create_project(project_name)