#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyGit - Automated GitHub Repository Creation & Initial Push Tool
Creates a GitHub repo matching the current folder name, configures git, and pushes.
"""

import os
import sys
import ssl
import json
import argparse
import subprocess
from pathlib import Path
from urllib import request, error

# Windows 콘솔 한글 깨짐 방지
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

CONFIG_DIR = Path.home() / ".easygit"
CONFIG_FILE = CONFIG_DIR / "config.json"
GITHUB_API_BASE = "https://api.github.com"


def get_ssl_context():
    """Create SSL context, falling back gracefully if local cert store is missing."""
    try:
        return ssl.create_default_context()
    except Exception:
        ctx = ssl._create_unverified_context()
        return ctx


def run_cmd(cmd, cwd=None, check=True, capture=True):
    """Run a shell command and return stdout string."""
    try:
        res = subprocess.run(
            cmd,
            cwd=cwd or Path.cwd(),
            shell=True,
            check=check,
            capture_output=capture,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        return res.stdout.strip() if res.stdout else ""
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.strip() if e.stderr else str(e)
        raise RuntimeError(f"Command failed: {cmd}\nError: {err_msg}")


def check_git_installed():
    """Verify that git CLI is installed and accessible."""
    try:
        run_cmd("git --version")
    except Exception:
        print("[오류] Git이 설치되어 있지 않거나 PATH에 등록되지 않았습니다.")
        print("https://git-scm.com 에서 Git을 설치한 후 다시 시도해주세요.")
        sys.exit(1)


def load_saved_token():
    """Load token from environment variable or local config file."""
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token.strip()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("github_token", "").strip()
        except Exception:
            pass
    return None


def save_token(token):
    """Save GitHub token to local config."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"github_token": token.strip()}, f, indent=2)


def reset_token():
    """Delete saved token config."""
    if CONFIG_FILE.exists():
        try:
            CONFIG_FILE.unlink()
            print("[알림] 저장된 GitHub 토큰이 삭제되었습니다.")
        except Exception as e:
            print(f"[오류] 토큰 삭제 실패: {e}")
    else:
        print("[알림] 저장된 토큰이 없습니다.")


def get_app_dir():
    """Return directory of running executable or script."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def is_double_clicked():
    """Detect if the console was launched via Windows GUI double-click."""
    if not sys.platform.startswith("win"):
        return False
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        pids = (ctypes.c_uint * 2)()
        count = kernel32.GetConsoleProcessList(pids, 2)
        return count <= 2
    except Exception:
        return False


def update_powershell_profiles(action="install"):
    """Register or remove 'easygit' and '.\\easygit' in PowerShell profiles."""
    profile_dirs = [
        Path.home() / "Documents" / "WindowsPowerShell",
        Path.home() / "Documents" / "PowerShell"
    ]
    target_exe = str(get_app_dir() / "easygit.exe")
    fn_code = (
        "\n# EasyGit CLI Integration\n"
        f'function easygit {{ & "{target_exe}" @args }}\n'
        f'function .\\easygit {{ & "{target_exe}" @args }}\n'
    )

    for pdir in profile_dirs:
        profile_file = pdir / "Microsoft.PowerShell_profile.ps1"
        try:
            if action == "install":
                pdir.mkdir(parents=True, exist_ok=True)
                existing = profile_file.read_text(encoding="utf-8") if profile_file.exists() else ""
                # 기존 구버전 함수 제거 후 최신 등록
                cleaned = existing.replace("# EasyGit alias for .\\easygit\nfunction .\\easygit { & easygit @args }\n", "")
                if "# EasyGit CLI Integration" not in cleaned:
                    cleaned += fn_code
                profile_file.write_text(cleaned, encoding="utf-8")
            elif action == "uninstall" and profile_file.exists():
                existing = profile_file.read_text(encoding="utf-8")
                cleaned = existing.replace(fn_code, "").replace(
                    "# EasyGit alias for .\\easygit\nfunction .\\easygit { & easygit @args }\n", ""
                )
                profile_file.write_text(cleaned, encoding="utf-8")
        except Exception:
            pass


def install_to_path(verbose=True):
    """Register EasyGit directory to system PATH / shell profile."""
    target_dir = str(get_app_dir())
    script_path = str(get_app_dir() / "easygit.py")

    if sys.platform.startswith("win"):
        update_powershell_profiles("install")
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_ALL_ACCESS)
        except Exception as e:
            if verbose:
                print(f"[오류] 레지스트리 접근 실패: {e}")
            return

        try:
            current_path, reg_type = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current_path, reg_type = "", winreg.REG_EXPAND_SZ

        paths = [p for p in current_path.split(";") if p]
        if any(p.rstrip("\\/").lower() == target_dir.rstrip("\\/").lower() for p in paths):
            if verbose:
                print("=" * 60)
                print("  EasyGit 전역 명령어(PATH) 등록")
                print("=" * 60)
                print(f"[알림] 이미 사용자 PATH에 등록되어 있습니다:")
                print(f"  {target_dir}\n")
                print("새 터미널(CMD/PowerShell)을 열고 'easygit'을 실행해보세요.")
            winreg.CloseKey(key)
            return

        paths.append(target_dir)
        new_path = ";".join(paths)
        try:
            winreg.SetValueEx(key, "Path", 0, reg_type, new_path)
            winreg.CloseKey(key)

            # Broadcast WM_SETTINGCHANGE
            try:
                import ctypes
                HWND_BROADCAST = 0xFFFF
                WM_SETTINGCHANGE = 0x001A
                SMTO_ABORTIFHUNG = 0x0002
                result = ctypes.c_long()
                ctypes.windll.user32.SendMessageTimeoutW(
                    HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment",
                    SMTO_ABORTIFHUNG, 5000, ctypes.byref(result)
                )
            except Exception:
                pass

            if verbose:
                print("=" * 60)
                print("  EasyGit 전역 명령어(PATH) 등록")
                print("=" * 60)
                print("[성공] 사용자 PATH 및 PowerShell 프로필 등록 완료!")
                print(f"  -> 등록 경로: {target_dir}\n")
                print("▶ 새 터미널(CMD/PowerShell) 창에서는 바로 'easygit'을 사용할 수 있습니다.")
                print("▶ 현재 열려 있는 PowerShell 창에서 바로 쓰시려면 아래 명령어를 실행하세요:")
                print("   . $PROFILE")
            else:
                print(f"[자동 환경 설정] 시스템 PATH 및 PowerShell 프로필에 자동 등록되었습니다 ({target_dir})")
        except Exception as e:
            if verbose:
                print(f"[오류] PATH 등록 실패: {e}")
    else:
        # macOS / Linux (zsh / bash 지원)
        rc_files = [Path.home() / ".zshrc", Path.home() / ".bashrc"]
        alias_line = f'alias easygit="python3 \\"{script_path}\\""\n'
        for rc in rc_files:
            try:
                content = rc.read_text(encoding="utf-8") if rc.exists() else ""
                if "alias easygit=" not in content:
                    with open(rc, "a", encoding="utf-8") as f:
                        f.write(f"\n# EasyGit CLI\n{alias_line}")
            except Exception:
                pass

        try:
            os.chmod(script_path, 0o755)
        except Exception:
            pass

        if verbose:
            print("=" * 60)
            print("  EasyGit 전역 명령어(alias) 등록 (macOS/Linux)")
            print("=" * 60)
            print(f"[성공] ~/.zshrc 및 ~/.bashrc에 'easygit' alias 등록 완료!")
            print(f"  -> 실행 파일: {script_path}\n")
            print("▶ 새 터미널을 열거나 'source ~/.zshrc'를 실행하면 바로 'easygit'을 사용할 수 있습니다.")
        else:
            print(f"[자동 환경 설정] shell profile에 easygit alias가 등록되었습니다.")


def ensure_installed():
    """Silently check and install to PATH/profile if needed."""
    target_dir = str(get_app_dir())

    if sys.platform.startswith("win"):
        needs_install = False
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ)
            try:
                current_path, _ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current_path = ""
            winreg.CloseKey(key)

            paths = [p for p in current_path.split(";") if p]
            if not any(p.rstrip("\\/").lower() == target_dir.rstrip("\\/").lower() for p in paths):
                needs_install = True
        except Exception:
            pass

        profile_dirs = [
            Path.home() / "Documents" / "WindowsPowerShell",
            Path.home() / "Documents" / "PowerShell"
        ]
        for pdir in profile_dirs:
            pfile = pdir / "Microsoft.PowerShell_profile.ps1"
            if not pfile.exists():
                needs_install = True
                break
            try:
                if "# EasyGit CLI Integration" not in pfile.read_text(encoding="utf-8"):
                    needs_install = True
                    break
            except Exception:
                pass

        if needs_install:
            install_to_path(verbose=False)
    else:
        # macOS / Linux
        zshrc = Path.home() / ".zshrc"
        if not zshrc.exists() or "alias easygit=" not in zshrc.read_text(encoding="utf-8", errors="ignore"):
            install_to_path(verbose=False)


def uninstall_from_path():
    """Remove EasyGit directory from system PATH / shell profile and clean up config."""
    target_dir = str(get_app_dir())

    print("=" * 60)
    print("  EasyGit 제거 (Uninstall)")
    print("=" * 60)

    if sys.platform.startswith("win"):
        update_powershell_profiles("uninstall")
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_ALL_ACCESS)
        except Exception as e:
            print(f"[오류] 레지스트리 접근 실패: {e}")
            return

        try:
            current_path, reg_type = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current_path, reg_type = "", winreg.REG_EXPAND_SZ

        paths = [p for p in current_path.split(";") if p]
        filtered_paths = [
            p for p in paths
            if p.rstrip("\\/").lower() != target_dir.rstrip("\\/").lower()
        ]

        if len(paths) == len(filtered_paths):
            print(f"[알림] 사용자 PATH에 등록되어 있지 않습니다: {target_dir}")
        else:
            new_path = ";".join(filtered_paths)
            try:
                winreg.SetValueEx(key, "Path", 0, reg_type, new_path)
                # Broadcast WM_SETTINGCHANGE
                try:
                    import ctypes
                    HWND_BROADCAST = 0xFFFF
                    WM_SETTINGCHANGE = 0x001A
                    SMTO_ABORTIFHUNG = 0x0002
                    result = ctypes.c_long()
                    ctypes.windll.user32.SendMessageTimeoutW(
                        HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment",
                        SMTO_ABORTIFHUNG, 5000, ctypes.byref(result)
                    )
                except Exception:
                    pass
                print(f"[성공] 사용자 PATH에서 EasyGit이 제거되었습니다.")
            except Exception as e:
                print(f"[오류] PATH 제거 실패: {e}")

        winreg.CloseKey(key)
    else:
        # macOS / Linux
        rc_files = [Path.home() / ".zshrc", Path.home() / ".bashrc"]
        for rc in rc_files:
            if rc.exists():
                try:
                    lines = rc.read_text(encoding="utf-8").splitlines()
                    filtered = [l for l in lines if "EasyGit" not in l and "alias easygit=" not in l]
                    rc.write_text("\n".join(filtered) + "\n", encoding="utf-8")
                except Exception:
                    pass
        print("[성공] ~/.zshrc 및 ~/.bashrc에서 EasyGit 등록이 제거되었습니다.")

    # 설정 파일(토큰) 삭제 안내/정리
    if CONFIG_DIR.exists():
        try:
            for item in CONFIG_DIR.iterdir():
                item.unlink()
            CONFIG_DIR.rmdir()
            print(f"[완료] 저장된 설정 및 토큰 폴더(~/.easygit)가 삭제되었습니다.")
        except Exception as e:
            print(f"[알림] 설정 폴더 삭제 실패: {e}")

    print("\nEasyGit 제거가 완료되었습니다.")


def github_request(endpoint, token, method="GET", data=None):
    """Send an authenticated HTTP request to GitHub API."""
    url = f"{GITHUB_API_BASE}{endpoint}" if endpoint.startswith("/") else endpoint
    payload = json.dumps(data).encode("utf-8") if data else None

    req = request.Request(url, data=payload, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "EasyGit-Tool")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data:
        req.add_header("Content-Type", "application/json")

    ctx = get_ssl_context()
    try:
        with request.urlopen(req, context=ctx) as res:
            res_body = res.read().decode("utf-8")
            return json.loads(res_body) if res_body else {}
    except error.HTTPError as e:
        err_content = e.read().decode("utf-8", errors="replace")
        try:
            err_json = json.loads(err_content)
            message = err_json.get("message", err_content)
        except Exception:
            message = err_content
        if "Resource not accessible by personal access token" in message:
            message += "\n -> 원인: 토큰 권한 부족 (새 저장소 생성 권한 없음)"
            message += "\n -> [해결방법 1] Classic 토큰(권장): https://github.com/settings/tokens/new?scopes=repo&description=EasyGit (repo 권한 1개만 체크)"
            message += "\n -> [해결방법 2] Fine-grained 토큰 사용 시:"
            message += "\n    1) Repository access를 반드시 'All repositories'로 설정"
            message += "\n    2) Repository permissions에서 'Administration' 및 'Contents'를 'Read and write'로 설정"
        raise RuntimeError(f"GitHub API Error ({e.code}): {message}")
    except error.URLError as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            try:
                unverified_ctx = ssl._create_unverified_context()
                with request.urlopen(req, context=unverified_ctx) as res:
                    res_body = res.read().decode("utf-8")
                    return json.loads(res_body) if res_body else {}
            except Exception as retry_err:
                raise RuntimeError(f"네트워크 오류: {retry_err}")
        raise RuntimeError(f"네트워크 연결 오류: {e.reason}")


def verify_token(token):
    """Verify token validity and return authenticated username."""
    try:
        data = github_request("/user", token)
        return data.get("login")
    except Exception as e:
        return None


def prompt_and_save_token():
    """Prompt user for GitHub token and validate before saving."""
    print("=" * 60)
    print(" GitHub Personal Access Token (PAT) 설정 (최초 1회 전역 설정)")
    print("=" * 60)
    print("▶ 토큰은 최초 1회만 등록하면 PC 전체에 '전역(Global)'으로 저장됩니다.")
    print("▶ 프로젝트마다 새로 생성할 필요 없이, 모든 폴더에서 자동 재사용됩니다.")
    print("▶ [주의] 반드시 'Classic' 토큰(ghp_...)을 사용해야 합니다.")
    print("  (GitHub 정책상 Fine-grained 토큰은 새 레포 생성을 허용하지 않습니다)")
    print("-" * 60)
    print("Classic 토큰 발급 방법:")
    print(" 1. 링크 접속: https://github.com/settings/tokens/new?scopes=repo&description=EasyGit")
    print(" 2. 'repo' 권한 체크 확인 후 하단 [Generate token] 클릭")
    print(" 3. 생성된 'ghp_...' 토큰 복사 후 아래에 붙여넣기")
    print("=" * 60)

    while True:
        token = input("GitHub Token 입력: ").strip()
        if not token:
            print("[경고] 토큰을 입력해야 계속 진행할 수 있습니다.")
            continue

        if token.startswith("github_pat_"):
            print(" -> Fine-grained 토큰이 감지되었습니다.")
            print("    (주의: 'Repository access'가 'All repositories'여야 하며,")
            print("     'Administration'과 'Contents' 권한이 'Read and write'여야 합니다.)")

        print("토큰 검증 중...")
        username = verify_token(token)
        if username:
            save_token(token)
            print(f"[성공] 인증되었습니다! 사용자: @{username}")
            print(f"[전역 저장 완료] 다음부터는 다른 프로젝트 폴더에서도 토큰 입력 없이 바로 실행됩니다.")
            print(f" -> 저장 위치: {CONFIG_FILE}\n")
            return token, username
        else:
            print("[오류] 유효하지 않은 토큰입니다. 권한과 토큰 값을 다시 확인해주세요.\n")


def get_token():
    """Retrieve verified GitHub token and username."""
    token = load_saved_token()
    if token:
        username = verify_token(token)
        if username:
            source = "시스템 환경 변수(GITHUB_TOKEN)" if os.environ.get("GITHUB_TOKEN") else f"전역 설정 파일({CONFIG_FILE})"
            print(f"[전역 토큰 사용] 저장된 토큰으로 인증 완료 (@{username})")
            print(f" -> 토큰 출처: {source}")
            print(f" -> (토큰을 변경하려면 'easygit --reset-token' 실행)")
            return token, username
        print("[경고] 저장된 전역 토큰이 만료되었거나 유효하지 않습니다. 다시 입력해주세요.\n")

    return prompt_and_save_token()


def sanitize_repo_name(name):
    """Sanitize name to make it GitHub-safe."""
    cleaned = "".join(c if (c.isalnum() or c in "-_.") else "-" for c in name)
    cleaned = cleaned.strip(".-_")
    return cleaned or "my-new-project"


def ensure_not_empty(target_dir, repo_name):
    """Ensure repository has at least one file to commit."""
    items = list(target_dir.iterdir())
    # Exclude .git and easygit scripts from consideration
    meaningful = [
        it for it in items
        if it.name != ".git" and it.name not in ("easygit.py", "easygit.bat", "install.bat")
    ]
    if not meaningful:
        readme_path = target_dir / "README.md"
        if not readme_path.exists():
            readme_path.write_text(f"# {repo_name}\n\nProject initialized with EasyGit.\n", encoding="utf-8")
            print(f"[생성] 빈 폴더이므로 기본 README.md를 생성했습니다.")


def main():
    parser = argparse.ArgumentParser(description="EasyGit - 원클릭 GitHub 레포 생성 및 초기 푸시 도구")
    parser.add_argument("--name", "-n", help="생성할 GitHub 저장소 이름 (기본값: 현재 폴더명)")
    parser.add_argument("--public", action="store_true", help="저장소를 Public(공개)으로 생성")
    parser.add_argument("--private", action="store_true", help="저장소를 Private(비공개)으로 생성 (기본값)")
    parser.add_argument("--message", "-m", default="Initial commit", help="커밋 메시지 (기본값: 'Initial commit')")
    parser.add_argument("--reset-token", action="store_true", help="저장된 GitHub 토큰 초기화")
    parser.add_argument("--install", action="store_true", help="현재 폴더를 사용자 PATH 환경변수에 등록")
    parser.add_argument("--uninstall", action="store_true", help="사용자 PATH 및 설정에서 EasyGit 제거")
    parser.add_argument("--dir", "-d", default=".", help="대상 디렉토리 경로 (기본값: 현재 위치)")
    args = parser.parse_args()

    if args.uninstall:
        uninstall_from_path()
        sys.exit(0)

    if args.reset_token:
        reset_token()
        sys.exit(0)

    # 실행 시 전역 PATH 및 PowerShell 등록 상태 자동 확인 및 설치
    ensure_installed()

    if args.install:
        sys.exit(0)

    check_git_installed()

    target_dir = Path(args.dir).resolve()
    if not target_dir.is_dir():
        print(f"[오류] 대상 디렉토리가 존재하지 않습니다: {target_dir}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  EasyGit - GitHub 원스톱 저장소 초기화 도구")
    print("=" * 60)

    # 1. GitHub 인증
    token, username = get_token()

    # 2. 대상 폴더 확인 및 로컬 Git 사전 점검
    print(f"\n[대상 폴더] {target_dir}")
    is_git_repo = (target_dir / ".git").is_dir()
    if is_git_repo:
        print("[주의] 해당 폴더에 이미 로컬 Git 저장소(.git)가 초기화되어 있습니다.")
        confirm = input("기존 로컬 Git 환경을 유지한 채로 작업을 계속 진행하시겠습니까? (y/N) [기본값: N]: ").strip().lower()
        if confirm != "y":
            print("[중단] 사용자의 요청으로 작업을 안전하게 취소했습니다.")
            sys.exit(0)

    # 3. 저장소 이름 결정
    default_name = sanitize_repo_name(target_dir.name)
    if args.name:
        repo_name = sanitize_repo_name(args.name)
    else:
        user_name = input(f"GitHub 저장소 이름 입력 [기본값: {default_name}]: ").strip()
        repo_name = sanitize_repo_name(user_name) if user_name else default_name

    # 4. GitHub 원격 저장소 중복 여부 확인
    repo_data = None
    try:
        existing = github_request(f"/repos/{username}/{repo_name}", token=token)
        if existing and existing.get("name"):
            print(f"\n[주의] GitHub에 동일한 이름의 원격 저장소(@{username}/{repo_name})가 이미 존재합니다.")
            confirm = input("기존 원격 저장소에 연결하여 계속 진행하시겠습니까? (y/N) [기본값: N]: ").strip().lower()
            if confirm != "y":
                print("[중단] 사용자의 요청으로 작업을 안전하게 취소했습니다.")
                sys.exit(0)
            repo_data = existing
    except Exception:
        pass

    # 5. 공개 범위 (Visibility) 결정 및 원격 저장소 생성
    if not repo_data:
        if args.public:
            is_private = False
        elif args.private:
            is_private = True
        else:
            print("\n공개 범위(Visibility) 설정:")
            print("  1) Private (비공개 - 권장)")
            print("  2) Public  (공개)")
            choice = input("선택 [기본값: 1]: ").strip()
            is_private = (choice != "2")

        visibility_str = "Private (비공개)" if is_private else "Public (공개)"
        print(f"\n▶ 레포지토리: @{username}/{repo_name}")
        print(f"▶ 공개 범위: {visibility_str}")
        print(f"▶ 커밋 메시지: {args.message}")

        # GitHub 원격 저장소 생성 API 호출
        print("\n[1/5] GitHub에 새 저장소 생성 중...")
        try:
            repo_data = github_request(
                "/user/repos",
                token=token,
                method="POST",
                data={
                    "name": repo_name,
                    "private": is_private,
                    "auto_init": False
                }
            )
            print(f" -> 원격 저장소 생성 완료: {repo_data.get('html_url')}")
        except RuntimeError as e:
            if "name already exists" in str(e).lower():
                print(f"[주의] GitHub에 이미 '{repo_name}' 저장소가 존재합니다.")
                confirm = input("기존 원격 저장소에 연결하여 계속 진행하시겠습니까? (y/N) [기본값: N]: ").strip().lower()
                if confirm != "y":
                    print("[중단] 사용자의 요청으로 작업을 안전하게 취소했습니다.")
                    sys.exit(0)
                repo_data = github_request(f"/repos/{username}/{repo_name}", token=token)
            else:
                print(f"[오류] 저장소 생성 실패: {e}")
                sys.exit(1)
    else:
        print(f" -> 기존 원격 저장소에 연결합니다: {repo_data.get('html_url')}")

    html_url = repo_data.get("html_url")
    # 토큰 포함 원격 URL 구성 (HTTPS 푸시 인증 자동 통과)
    clone_url_with_token = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
    standard_clone_url = f"https://github.com/{username}/{repo_name}.git"

    # 5. 로컬 Git 초기화
    print("\n[2/5] 로컬 Git 초기화 확인 중...")
    is_git_repo = (target_dir / ".git").is_dir()
    if not is_git_repo:
        run_cmd("git init", cwd=target_dir)
        print(" -> git init 완료.")
    else:
        print(" -> 기존 .git 저장소 감지됨.")

    # 기본 브랜치 main으로 통일
    run_cmd("git branch -M main", cwd=target_dir)

    # 6. 원격 저장소 (remote origin) 설정
    print("\n[3/5] 원격 저장소(origin) 연결 중...")
    remotes = run_cmd("git remote", cwd=target_dir)
    if "origin" in remotes.split():
        run_cmd(f'git remote set-url origin "{clone_url_with_token}"', cwd=target_dir)
        print(" -> 기존 origin URL 갱신 완료.")
    else:
        run_cmd(f'git remote add origin "{clone_url_with_token}"', cwd=target_dir)
        print(" -> origin 등록 완료.")

    # 빈 폴더 방지
    ensure_not_empty(target_dir, repo_name)

    # 7. 파일 스테이징 및 커밋
    print("\n[4/5] 변경사항 커밋 중...")
    run_cmd("git add -A", cwd=target_dir)

    status = run_cmd("git status --porcelain", cwd=target_dir)
    if status:
        run_cmd(f'git commit -m "{args.message}"', cwd=target_dir)
        print(f" -> 커밋 완료 ('{args.message}')")
    else:
        # 커밋할 내역이 없는지 로그 확인
        has_commit = True
        try:
            run_cmd("git rev-parse HEAD", cwd=target_dir)
            print(" -> 새로 커밋할 변경사항이 없어 기존 커밋 상태를 유지합니다.")
        except RuntimeError:
            has_commit = False

        if not has_commit:
            # 강제로 초기 커밋 생성
            ensure_not_empty(target_dir, repo_name)
            run_cmd("git add -A", cwd=target_dir)
            run_cmd(f'git commit -m "{args.message}"', cwd=target_dir)
            print(f" -> 초기 커밋 생성 완료 ('{args.message}')")

    # 8. 원격 저장소로 푸시
    print("\n[5/5] GitHub로 푸시 중 (git push -u origin main)...")
    try:
        run_cmd("git push -u origin main", cwd=target_dir)
        print(" -> Push 완료!")
    except RuntimeError as e:
        print(f"[경고] 표준 푸시 실패. 재시도 중...\n{e}")
        try:
            # 원격에 파일이 이미 있을 경우 대비 --set-upstream
            run_cmd("git push --set-upstream origin main --force", cwd=target_dir)
            print(" -> 강제 푸시 완료!")
        except Exception as push_err:
            print(f"[오류] 푸시 실패: {push_err}")
            print("수동으로 'git push -u origin main'을 실행해보세요.")
            sys.exit(1)

    # 보안을 위해 origin URL을 토큰 없는 표준 URL로 재설정
    run_cmd(f'git remote set-url origin "{standard_clone_url}"', cwd=target_dir)

    print("\n" + "=" * 60)
    print(" 🎉 축하합니다! 모든 작업이 성공적으로 완료되었습니다.")
    print(f" 🔗 GitHub 저장소 URL: {html_url}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    exit_code = 0
    try:
        main()
    except KeyboardInterrupt:
        print("\n[취소] 사용자에 의해 작업이 중단되었습니다.")
    except Exception as e:
        print(f"\n[오류] 프로그램 실행 중 문제가 발생했습니다: {e}")
        exit_code = 1
    finally:
        if is_double_clicked():
            try:
                input("\n종료하려면 Enter 키를 누르세요...")
            except Exception:
                pass
    sys.exit(exit_code)
