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

echo "설치가 완료되었습니다. 터미널을 새로 열거나 'source ~/.zshrc'를 실행하세요."

