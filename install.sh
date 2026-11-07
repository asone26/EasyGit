#!/usr/bin/env bash
# EasyGit macOS / Linux One-Click Installer

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SCRIPT_PATH="$DIR/easygit.py"

echo "======================================================"
echo " EasyGit macOS / Linux 설치 도구"
echo "======================================================"

chmod +x "$SCRIPT_PATH"
python3 "$SCRIPT_PATH" --install


