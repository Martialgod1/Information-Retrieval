# PyLucene Development Environment

This project provides a Docker-based development environment for working with PyLucene in Python. The setup includes all necessary dependencies and configurations for a smooth development experience.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10.0 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 1.29.0 or higher)
- [Visual Studio Code](https://code.visualstudio.com/)
- [VS Code Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## Installation

1. Clone this repository:
   ```bash
   git clone <your-repository-url>
   cd <repository-name>
   ```

2. Open the project in VS Code:
   ```bash
   code .
   ```

3. Install the Remote - Containers extension in VS Code:
   - Press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows/Linux)
   - Search for "Remote - Containers"
   - Install the extension by Microsoft

4. Reopen the project in a container:
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Remote-Containers: Reopen in Container"
   - Select this option

VS Code will now build the Docker container and set up the development environment. This might take a few minutes on the first run.

## Project Structure

```
.
├── .devcontainer/
│   └── devcontainer.json    # VS Code container configuration
├── Dockerfile               # Docker build configuration
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
└── L1.py                    # Sample PyLucene application
```

## Running the Application

### Using VS Code

1. Once the container is built and running, you can use the integrated terminal in VS Code
2. The terminal will automatically be connected to the container
3. Run your Python scripts directly from the terminal

### Using Docker Compose

From your terminal, you can run:
```bash
docker-compose up
```

## Development

- All your local files are mounted into the container, so any changes you make will be reflected immediately
- The Python environment includes:
  - Python 3.9
  - PyLucene 9.8.0
  - Java 11
  - All necessary system dependencies

## VS Code Features

The development container includes:
- Python extension
- Pylance language server
- Autopep8 formatter
- Python linting

## Troubleshooting

If you encounter any issues:

1. Check Docker is running:
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

## License

[Your License Here]

## Contributing

[Your Contribution Guidelines Here]