# Space Invaders
# For Setup and run:

## 1. Install Python
Python 3.12 or newer is required. Install it for example via:
  ### Linux Debian/Ubuntu
  ```
  sudo apt install python3
  ```
  ### macOS using Homebrew
  ```
  brew install python
  ```
  ### Windows
  Download and install Python from the official website
  https://www.python.org/downloads/windows/
  
  Make sure to select „Add Python to PATH“ during installation.
## 2. Start virtual environment (optional)
  Using a virtual environment helps to isolate project dependencies from your system Python.
  ### Linux/macOS
  ```
  python3 -m venv spaceinvaders
  source spaceinvaders/bin/activate
  ```
  ### Windows (cmd)
  ```
  python -m venv spaceinvaders
  .\spaceinvaders\Scripts\activate
  ```
  You can later leave the virtual environment via `deactivate`.
## 3. Install dependencies (pygame)
  ```
  pip install -r requirements.txt
  ```
## 4. Run the game
  ```
  python main.py
  ```
## 5. Documentation
* To generate the documentation, install LaTeX
  ### Linux (Debian/Ubuntu)
  ```
  sudo apt install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended
  ```
  ### macOS using Homebrew
  ```
  brew install --cask basictex
  sudo tlmgr update --self
  sudo tlmgr install latex-recommended latex-extra collection-fontsrecommended
  ```
  ### Windows
  Download and install MiKTeX from https://miktex.org/download

* Install Sphinx
  ```
  pip install sphinx sphinx-autoapi
  ```
  and compile the documentation via
  `python documentation.py` or `python3 documentation.py`.

  You can then open `documentation.pdf` in the same directory.
