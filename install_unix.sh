#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Installing system libraries..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y zlib1g-dev build-essential pkg-config libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
elif command -v dnf &> /dev/null; then
    sudo dnf groupinstall -y "Development Tools"
    sudo dnf install -y zlib-devel zlib-ng-compat-devel sdl2-devel sdl2-compat-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel
elif command -v pacman &> /dev/null; then
    sudo pacman -S --needed --noconfirm base-devel zlib sdl2-compat sdl2 sdl2_image sdl2_mixer sdl2_ttf
elif command -v brew &> /dev/null; then
    brew install zlib sdl2 sdl2_image sdl2_mixer sdl2_ttf
fi

if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
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
echo "Installing requirements..."
python -m pip install --upgrade pip > /dev/null
python -m pip install -r requirements.txt

echo "#!/bin/bash" > start.sh
echo "cd \"\$(dirname \"\$0\")\"" >> start.sh
echo "source venv/bin/activate" >> start.sh
echo "python main.py" >> start.sh
chmod +x start.sh

echo ""
echo Installation complete. Open 'start.sh' to play!
echo Have fun and good luck beating the high scores!
echo ""
read -p "Press enter to exit..."