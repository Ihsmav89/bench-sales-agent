#!/bin/bash
# Bench Sales Agent — macOS Install Script
set -e

echo "========================================="
echo "  Bench Sales Agent — macOS Installer"
echo "========================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Install it from https://www.python.org/downloads/ or via Homebrew:"
    echo "  brew install python@3.12"
    exit 1
fi

PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]); then
    echo "ERROR: Python 3.11+ required. Found Python $PY_VERSION."
    exit 1
fi

echo "Found Python $PY_VERSION"

# Determine install directory
INSTALL_DIR="${HOME}/.bench-sales-agent"
echo "Installing to: $INSTALL_DIR"

# Create virtual environment
if [ -d "$INSTALL_DIR" ]; then
    echo "Existing installation found. Updating..."
else
    echo "Creating virtual environment..."
    python3 -m venv "$INSTALL_DIR/venv"
fi

# Activate and install
source "$INSTALL_DIR/venv/bin/activate"

echo "Installing Bench Sales Agent..."
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
pip install --upgrade pip -q
pip install "$SCRIPT_DIR" -q

# Create launch script
cat > "$INSTALL_DIR/start.sh" << 'LAUNCHER'
#!/bin/bash
source "${HOME}/.bench-sales-agent/venv/bin/activate"
bench-agent-web "$@"
LAUNCHER
chmod +x "$INSTALL_DIR/start.sh"

# Add alias to shell profile
SHELL_RC="${HOME}/.zshrc"
if [ -f "${HOME}/.bashrc" ] && [ ! -f "${HOME}/.zshrc" ]; then
    SHELL_RC="${HOME}/.bashrc"
fi

if ! grep -q "bench-agent-web" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Bench Sales Agent" >> "$SHELL_RC"
    echo "alias bench-agent-web='${INSTALL_DIR}/start.sh'" >> "$SHELL_RC"
    echo "Added 'bench-agent-web' alias to $SHELL_RC"
fi

echo ""
echo "========================================="
echo "  Installation Complete!"
echo "========================================="
echo ""
echo "To start the agent:"
echo "  ${INSTALL_DIR}/start.sh"
echo ""
echo "Or open a new terminal and run:"
echo "  bench-agent-web"
echo ""
echo "Optional: Set your API key for AI features:"
echo "  export ANTHROPIC_API_KEY=your-key-here"
echo ""
