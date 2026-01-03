# Space Invaders
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.5.2-green.svg)

## Description
This is a small space shooter game with five levels developed with **pygame**, a light-weight python framework.

## Setup and run the game

### 1. Install Python
**Python 3.11** or newer is required. Install it for example via:
  #### Linux Debian/Ubuntu
  ```
  sudo apt update
  sudo apt install python3 python3-venv
  ```
  #### macOS using Homebrew
  ```
  brew install python
  ```
  #### Windows
  Download and install **Python 3.11** or newer from the official website
  https://www.python.org/downloads/windows
  (`Windows installer 64-bit` for most systems)
  
  Make sure to select „**Add Python to PATH**“ during installation.

### 2. Run the game
  #### Windows
  Double-click `run_windows.bat`.
  #### macOS / Linux
  Open your terminal in the project folder.
  Grant execution permissions to the script (only required once):
  ```bash
  chmod +x run_unix.sh
  ```
  Then launch the game via
  ```bash
  ./run_unix.sh
  ```

## Documentation for developers
The documentation `Documentation.pdf` contains technical explanations of the relevant components of the game. It was compiled using **sphinx-autoapi**, **LaTeX** and the script in `documentation/documentation.py`.