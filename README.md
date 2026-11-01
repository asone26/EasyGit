# EasyGit 🚀

> **Guides / 가이드 문서**:
> - 🇰🇷 [한국어 사용자 가이드 (Korean User Guide)](file:///c:/Project/EasyGit/GUIDE_KO.md)
> - 🇺🇸 [English User Guide](file:///c:/Project/EasyGit/GUIDE_EN.md)
> - 📋 [Master Specification (마스터 정의서)](file:///c:/Project/EasyGit/master.md)

신규 프로젝트 폴더에서 **폴더명 기반 GitHub 레포 생성**, **Private/Public 선택**, **로컬 Git 초기화**, **커밋**, **푸시**를 한 번에 끝내는 원스톱 도구입니다.

---

## 주요 기능

1. **폴더명 자동 인식**: 현재 디렉토리명을 GitHub 레포지토리 기본 이름으로 추천.
2. **공개 범위 선택**: `Private (비공개, 기본값)` 또는 `Public (공개)` 간편 선택.
3. **토큰 1회 저장**: GitHub Personal Access Token(PAT)을 최초 1회만 입력하면 `~/.easygit/config.json`에 저장하여 이후 자동 인증.
4. **원클릭 자동화**:
   - GitHub 원격 레포지토리 API 생성
   - `git init` & 기본 브랜치 `main` 설정
   - 원격 저장소(`origin`) 등록
   - `git add -A` 및 초기 커밋(`git commit -m`)
   - `git push -u origin main` 완료 후 저장소 URL 출력
5. **무설치/의존성 제로**: Python 표준 라이브러리(`urllib`)만 사용하여 추가 pip 패키지 설치 필요 없음.

---

## 사용 방법

### 방법 1. 그냥 실행하기 (자동 전역 등록 지원 ⭐)
`easygit.exe`를 실행하면, **전역 환경(PATH 및 PowerShell)에 등록되어 있는지 스스로 확인**하여:
- 아직 등록되어 있지 않다면 최초 1회 자동 등록합니다.
- 이미 등록되어 있다면 바로 Git 초기화 작업으로 넘어갑니다.

등록 후에는 어떤 폴더에서든 터미널을 열고 `easygit`을 입력하시면 됩니다.

### 방법 2. 프로젝트 폴더에서 직접 실행

- 신규 작업 폴더에 `easygit.bat` 또는 `easygit.py`를 복사한 후 더블클릭하거나 터미널에서 실행:
  ```bash
  python easygit.py
  ```

---

## 명령어 옵션 (CLI)

```bash
# 기본 대화형 모드
easygit

# Public으로 즉시 생성
easygit --public

# Private으로 즉시 생성 (기본값)
easygit --private

# 저장소 이름 및 커밋 메시지 직접 지정
easygit --name "my-cool-project" -m "feat: first release"

# 저장된 GitHub 토큰 초기화
easygit --reset-token

# 설치 제거 (사용자 PATH 및 저장된 토큰 정리)
easygit --uninstall
```

---

## 최초 1회 GitHub Token 발급 및 등록 안내

- **전역(Global) 1회 등록**: 토큰은 프로젝트마다 생성할 필요가 없으며, 최초 1회만 등록하면 PC 전체에 저장되어 모든 프로젝트 폴더에서 재사용됩니다.
- **기존 토큰 재사용**: 이미 사용 중인 GitHub 토큰(`repo` 권한 포함)이 있다면 새로 생성할 필요 없이 그대로 입력하시면 됩니다.

새로 발급받아야 하는 경우:
1. [GitHub Personal Access Tokens 페이지](https://github.com/settings/tokens/new?scopes=repo&description=EasyGit) 접속
2. `Note`에 `EasyGit` 입력 후 `repo` 체크박스 선택 (기본 체크됨)
3. 맨 아래 `Generate token` 클릭 후 생성된 토큰 복사
4. EasyGit 실행 시 입력창에 붙여넣기 (최초 1회만 입력하면 저장됨)

