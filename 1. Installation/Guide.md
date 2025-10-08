# PyLucene Development Environment Setup Guide

This guide provides instructions for setting up a Docker-based development environment for working with PyLucene in Python. The setup includes all necessary dependencies and configurations for a smooth development experience.

## Table of Contents
- [MacOS Setup](#macos-setup)
- [Windows Setup](#windows-setup)
- [Project Structure](#project-structure)
- [Running the Application](#running-the-application)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Configuration Files Setup](#configuration-files-setup)

## MacOS Setup

1. Install Homebrew (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install required packages:
   ```bash
   brew install coady/tap/pylucene
   brew install python3
   ```

3. Run the test application:
   ```bash
   /opt/homebrew/bin/python3 test.py
   ```

## Windows Setup

### Prerequisites

1. Install Docker Desktop:
   - Download from [Docker's official website](https://www.docker.com/)

2. Install VS Code Extensions:
   - [Dev Containers](https://marketplace.visualstudio.com/items/?itemName=ms-vscode-remote.remote-containers)
   - [Docker](https://marketplace.visualstudio.com/items/?itemName=ms-azuretools.vscode-docker)
   - [Docker DX](https://marketplace.visualstudio.com/items/?itemName=docker.docker)

### Installation Steps

1. Start Docker Container:
   ```bash
   docker run -it coady/pylucene
   ```

2. Open the project directory in VS Code

3. Install Remote - Containers extension:
   - Press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows/Linux)
   - Search for "Remote - Containers"
   - Install the extension by Microsoft

4. Reopen project in container:
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Remote-Containers: Reopen in Container"
   - Select this option

VS Code will build the Docker container and set up the development environment. This might take a few minutes on the first run.

## Project Structure

```
.
├── .devcontainer/
│   └── devcontainer.json    # VS Code container configuration
├── Dockerfile               # Docker build configuration
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
└── test.py                  # Sample PyLucene application
```

## Running the Application

1. Open VS Code terminal
2. Navigate to your project directory
3. Ensure Docker is running
4. Execute the following command:
   ```bash
   docker-compose up --build
   ```

## Development

- All local files are mounted into the container, so any changes you make will be reflected immediately
- The Python environment includes:
  - Python 3.9
  - PyLucene 9.8.0
  - Java 11
  - All necessary system dependencies

## Troubleshooting

If you encounter any issues:

1. Check Docker status:
   ```bash
   docker info
   ```

2. Rebuild the container:
   ```bash
   docker-compose build --no-cache
   ```

3. Check container logs:
   ```bash
   docker-compose logs
   ```

4. Verify container is running:
   ```bash
   docker ps
   ```

5. If issues persist, try restarting Docker Desktop and VS Code

## Configuration Files Setup

> **What is a Dev Container?**
> 
> A Dev Container (Development Container) is a Docker container that's specifically configured to provide a complete development environment. The `.devcontainer` configuration files tell VS Code how to:
> - Build and run your development container
> - Configure the development environment
> - Install necessary extensions
> - Set up workspace settings
> - Mount your project files
> 
> **Benefits of using Dev Containers:**
> - Consistent development environment across all team members
> - Pre-configured development tools and extensions
> - Isolated development environment
> - Easy to share and reproduce development setup
> - Seamless integration with VS Code features

1. Create a `.devcontainer` directory in your project root:
   ```bash
   mkdir .devcontainer
   ```

2. Copy the following files to your project:
   - Copy `docker-compose.yml` to your project root
   - Copy `devcontainer.json` to the `.devcontainer` directory

3. Update the paths in `docker-compose.yml`:
   ```yaml
   services:
     app:
       build: .
       volumes:
         - /path/to/your/project:/app  # Update this path
       environment:
         - PYTHONPATH=/app
       command: python3 test.py
   ```

4. Update the paths in `.devcontainer/devcontainer.json`:
   ```json
   {
     "name": "PyLucene Development",
     "dockerComposeFile": "../docker-compose.yml",
     "service": "app",
     "workspaceFolder": "/app",
     "customizations": {
       "vscode": {
         "extensions": [
           "ms-python.python"
         ]
       }
     }
   }
   ```

5. Make sure the paths in both files point to your project directory:
   - In `docker-compose.yml`, update the volume mount path to your project's absolute path
   - In `devcontainer.json`, ensure the `workspaceFolder` matches your project structure

6. Verify the configuration:
   - The paths should be absolute paths to your project
   - The workspace folder in devcontainer.json should match your project's root directory
   - All file permissions should be correct

## Run Commands (PyLucene)

Use these from the `3. PyLucene` folder (containerized with docker-compose):

```bash
cd "/Users/pray/Documents/Information-Retrieval/3. PyLucene"

# 1) Index (clean and index)
docker-compose run --rm app bash -lc 'rm -rf /app/index && python3 indexer.py --source "/app" --index /app/index'

# Optional: try codec best-compression (falls back if unavailable)
docker-compose run --rm app python3 indexer.py --source "/app" --index /app/index --best-compression

# 2) BM25 ranked retrieval
docker-compose run --rm app python3 search_bm25.py --index /app/index --query "index compression"

# 3) Boolean retrieval
docker-compose run --rm app python3 search_boolean.py --index /app/index --query "inverted AND index"
docker-compose run --rm app python3 search_boolean.py --index /app/index --query '"vector space" OR compression'

# 4) VSM / TF-IDF
docker-compose run --rm app python3 search_vsm.py --index /app/index --query "vector space model" --topk 10

# 5) Axiomatic retrieval (variants: F2EXP | F2LOG | F1EXP | F1LOG)
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "term weighting" --variant F2EXP
docker-compose run --rm app python3 search_axiomatic.py --index /app/index --query "term weighting" --variant F2LOG

# Common optional flags
# --field contents  (change field)
# --topk 20         (change number of results)
```

