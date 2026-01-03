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
  Double-click `install_windows.bat` to install the game and then `start.bat` to play.
  #### macOS / Linux
  Open your terminal in the project folder, run
  ```bash
  ./install_unix.sh
  ```
  to install the game and then
  ```bash
  ./start.sh
  ```
  to play.

### Alternative / Trouble shooting
If the automated scripts do not work for you or graphics / sounds are missing, follow these steps:
* If you are using **Linux / macOS**, install the following system libraries with your package manager:
  * **Debian/Ubuntu**: zlib1g-dev build-essential pkg-config libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
  * **Fedora**: zlib-devel SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel
  * **Arch**: zlib sdl2 sdl2_image sdl2_mixer sdl2_ttf
* Ensure you have **Python 3.11** or newer and install the package **pygame 2.5.2**.
* Run `python main.py`.

## Documentation for developers
The documentation `Documentation.pdf` contains technical explanations of the relevant components of the game. It was compiled using **sphinx-autoapi**, **LaTeX** and the script in `documentation/documentation.py`.