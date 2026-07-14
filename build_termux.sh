#!/bin/bash
# Build for Android tablet (Termux/aarch64)
set -e

echo "=== Building ControlAlmacen for Termux ==="

# Install deps in Termux
pip install urwid openpyxl pyinstaller

# Build
pyinstaller build.spec --clean

echo "=== Build complete ==="
echo "Binary: dist/ControlAlmacen"
echo ""
echo "If binary fails, run directly:"
echo "  python main.py <usuario>"
