# EasyGit 사용자 가이드 (Korean)

새 프로젝트 폴더에서 폴더명을 기반으로 GitHub 원격 저장소를 생성하고, 로컬 Git 연동 및 첫 커밋/푸시까지 원스톱으로 처리하는 가이드입니다.

---

## 1. 사전 준비 (최초 1회만 필요)

### 1.1 Git 및 Python 설치 확인
- **Git**: [git-scm.com](https://git-scm.com) 설치 필요
- **Python**: 3.8 이상 설치 필요 (별도의 추가 패키지 설치는 필요 없음)

### 1.2 GitHub 토큰 발급 (Classic 또는 Fine-grained)

EasyGit은 **Classic 토큰**과 **Fine-grained 토큰** 모두 지원합니다.

#### 옵션 A. Personal Access Tokens (Classic) — [가장 추천 ⭐]
설정이 매우 간단하며 만료일 및 권한 충돌이 없습니다.
1. [GitHub Classic 토큰 발급 링크](https://github.com/settings/tokens/new?scopes=repo&description=EasyGit)에 접속
2. `repo` 범위(Scope) 체크 확인 후 하단 **[Generate token]** 클릭
3. 생성된 `ghp_...` 토큰 복사 후 사용

#### 옵션 B. Fine-grained Personal Access Tokens
최신 세분화 권한 토큰을 쓰고 싶다면 **반드시 아래 2가지 설정**을 해야 합니다:
1. **Repository access**: 반드시 **`All repositories`** 선택  
   *(기본값인 `Only select repositories`를 선택하면 아직 만들어지지 않은 새 저장소에 접근하지 못해 403 오류가 발생합니다)*
2. **Repository permissions**:
   - `Administration`: **`Read and write`** (저장소 생성 권한)
   - `Contents`: **`Read and write`** (코드 커밋/푸시 권한)

---

## 2. 설치 및 설정

### 2.1 전역 명령어 등록 (어디서나 실행하기)
1. `c:\Project\EasyGit\install.bat` 파일을 더블클릭합니다.
2. 현재 EasyGit 폴더가 Windows 사용자 `PATH`에 등록됩니다.
3. 새 터미널 창을 열면 어떤 디렉토리에서든 `easygit` 명령어를 사용할 수 있습니다.

### 2.2 설치 제거 (삭제 방법)
- **자동 제거**: `c:\Project\EasyGit\uninstall.bat`을 더블클릭하거나 터미널에서 `easygit --uninstall`을 실행합니다.
  - 사용자 `PATH`에서 EasyGit 경로가 자동 제거됩니다.
  - 저장된 설정 및 GitHub 토큰(`~/.easygit`)도 함께 정리됩니다.
- **수동 제거**:
  1. Windows 검색창에 `시스템 환경 변수 편집` 검색 후 실행
  2. 하단 `[환경 변수(N)...]` 클릭
  3. `사용자 변수` 목록의 `Path` 선택 후 `[편집(E)...]` 클릭
  4. `C:\Project\EasyGit` 항목을 찾아 `[삭제]` 클릭 후 확인
  5. 필요시 내 컴퓨터의 `C:\Users\<사용자명>\.easygit` 폴더 삭제

---

## 3. 기본 사용법

### 3.1 대화형 모드 (기본 실행)
새로 시작할 프로젝트 디렉토리로 이동한 뒤 터미널에 입력합니다:

```bash
easygit
```

#### 진행 단계:
1. **GitHub Token 입력** (최초 1회만):
   - 발급해 둔 토큰을 붙여넣고 엔터를 누릅니다.
   - 검증 후 `~/.easygit/config.json`에 저장되어 다음부터는 묻지 않습니다.
2. **저장소 이름 확인**:
   - 현재 폴더명이 기본값으로 추천됩니다.
   - 그대로 쓰려면 `Enter`를 누르고, 다른 이름을 원하면 입력 후 `Enter`를 누릅니다.
3. **공개 범위(Visibility) 선택**:
   - `1) Private (비공개, 기본값)` : `Enter` 누르면 적용
   - `2) Public (공개)` : `2` 입력 후 `Enter`
4. **자동 처리 진행**:
   - GitHub 원격 레포 생성
   - 로컬 `git init` 및 `main` 브랜치 설정
   - 원격 저장소(`origin`) 연결
   - 파일 스테이징(`git add -A`) 및 초기 커밋(`git commit`)
   - `git push -u origin main` 완료 후 브라우저 접속 URL 출력

---

## 4. CLI 명령행 옵션

스크립트나 단일 명령어로 즉시 실행할 때 유용한 옵션입니다.

| 옵션 | 단축 옵션 | 설명 | 사용 예시 |
| :--- | :--- | :--- | :--- |
| `--public` | | 저장소를 공개(Public)로 생성 | `easygit --public` |
| `--private` | | 저장소를 비공개(Private)로 생성 (기본값) | `easygit --private` |
| `--name` | `-n` | 생성할 저장소 이름 직접 지정 | `easygit --name "my-app"` |
| `--message` | `-m` | 초기 커밋 메시지 지정 | `easygit -m "feat: first setup"` |
| `--dir` | `-d` | 작업할 대상 폴더 경로 지정 | `easygit -d "D:\workspace\new-project"` |
| `--reset-token` | | 저장된 GitHub 토큰 삭제 및 초기화 | `easygit --reset-token` |

#### 조합 예시:
```bash
# 비공개 레포지토리로 즉시 초기화 및 커밋/푸시
easygit --private -m "Initial release"

# 특정 디렉토리를 my-service라는 이름의 공개 레포로 생성
easygit -d "c:\temp\new-site" --name "my-service" --public
```

---

## 5. 문제 해결 (FAQ)

- **Q. 토큰을 다시 입력하거나 변경하고 싶어요.**
  - `easygit --reset-token`을 실행하면 저장된 토큰이 삭제되며 다음 실행 시 다시 입력받습니다.
- **Q. 이미 GitHub에 동일한 이름의 레포가 존재한다는 에러가 뜹니다.**
  - 기존 저장소에 연결할 것인지 묻는 프롬프트에서 `y`를 선택하면 기존 레포에 origin을 연결하고 push합니다.
- **Q. 빈 폴더인데 커밋할 파일이 없다고 오류가 나지 않나요?**
  - 폴더가 비어 있을 경우 EasyGit이 자동으로 `# [프로젝트명]` 헤더가 포함된 기본 `README.md`를 생성한 후 커밋/푸시합니다.

