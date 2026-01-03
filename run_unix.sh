#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! ldconfig -p 2>/dev/null | grep -q libz.so.1 && ! [ -f /usr/lib/libz.dylib ]; then
    echo "Installing system dependencies..."
    
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu/Mint
        sudo apt-get update && sudo apt-get install -y zlib1g
    elif command -v dnf &> /dev/null; then
        # Fedora
        sudo dnf install -y zlib-devel
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        sudo pacman -S --noconfirm zlib
    elif command -v brew &> /dev/null; then
        # macOS with Homebrew
        brew install zlib
    else
        echo "Warning: Could not detect package manager. Please install 'zlib' manually."
    fi
fi

if command -v python3 &> /dev/null && python3 -c "import sys; exit(0 if sys.version_info[:2] >= (3,11) else 1)" &> /dev/null; then
    PYTHON_EXE="python3"
elif command -v python3.11 &> /dev/null; then
    PYTHON_EXE="python3.11"
else
    echo ""
    echo "This game requires Python 3.11 or higher to run."
    echo "Please install it using your package manager, e.g. run:"
    echo "sudo apt update"
    echo "sudo apt install python3 python3-venv"
    echo "if you are using Linux or"
    echo "brew install python"
    echo "for macOS with Homebrew."
    echo ""
    read -p "Press enter to exit..."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_EXE -m venv venv
    if [ ! -f "venv/bin/activate" ]; then
        echo "ERROR: Virtual environment could not be created."
        echo "On Linux, you might need to install the venv package:"
        echo "sudo apt install python3-venv"
        read -p "Press enter to exit..."
        exit 1
    fi
    source venv/bin/activate
    echo "Checking requirements..."
    python -m pip install --upgrade pip > /dev/null
    python -m pip install -r requirements.txt
fi

source venv/bin/activate
python main.py