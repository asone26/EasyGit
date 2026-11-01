# EasyGit User Guide (English)

A one-stop automation tool to create a GitHub repository based on your project folder name, choose its visibility (Private/Public), initialize local Git, commit, and push in a single step.

---

## 1. Prerequisites (One-Time Setup)

### 1.1 Git and Python
- **Git**: Installed from [git-scm.com](https://git-scm.com)
- **Python**: Version 3.8 or higher (No third-party packages required)

### 1.2 GitHub Personal Access Token (PAT)
Required for calling the GitHub REST API to create repositories and authenticate git pushes.
1. Visit the [GitHub Token Generation Page](https://github.com/settings/tokens/new?scopes=repo&description=EasyGit).
2. Set the `Note` to `EasyGit`.
3. Ensure the `repo` scope is checked (Full control of private repositories).
4. Scroll to the bottom and click **[Generate token]**.
5. Copy the generated token string (`ghp_...`).

---

## 2. Installation & PATH Setup

### 2.1 Register Global Command (Run from anywhere)
1. Double-click `c:\Project\EasyGit\install.bat`.
2. This adds the EasyGit directory to your Windows user `PATH`.
3. Open a new terminal window. You can now use the `easygit` command from any folder.

### 2.2 Uninstallation
- **Automatic**: Double-click `c:\Project\EasyGit\uninstall.bat` or run `easygit --uninstall`.
  - Removes EasyGit from your User `PATH`.
  - Cleans up saved configuration and GitHub token (`~/.easygit`).
- **Manual**:
  1. Search for `Edit the system environment variables` in the Windows Start menu.
  2. Click **Environment Variables...**.
  3. Under **User variables**, select `Path` and click **Edit...**.
  4. Select `C:\Project\EasyGit` and click **Delete**.
  5. Delete `C:\Users\<username>\.easygit` directory if desired.

---

## 3. Basic Usage

### 3.1 Interactive Mode (Default)
Navigate to your project directory in terminal and run:

```bash
easygit
```

#### Step-by-step Flow:
1. **GitHub Token Prompt** (First run only):
   - Paste your GitHub PAT and press `Enter`.
   - Verified and stored securely in `~/.easygit/config.json`.
2. **Repository Name**:
   - Defaults to the current directory name.
   - Press `Enter` to accept the default or type a custom name.
3. **Visibility Selection**:
   - `1) Private (Default)` : Press `Enter` to choose Private
   - `2) Public` : Type `2` and press `Enter`
4. **Automated Pipeline**:
   - Creates remote repository on GitHub
   - Runs `git init` and sets default branch to `main`
   - Configures `origin` remote URL
   - Stages files (`git add -A`) and commits (`git commit`)
   - Pushes to remote (`git push -u origin main`) and prints the repo URL

---

## 4. CLI Command-Line Options

For automated scripts or quick single-line executions.

| Option | Shorthand | Description | Example |
| :--- | :--- | :--- | :--- |
| `--public` | | Create the repository as Public | `easygit --public` |
| `--private` | | Create the repository as Private (Default) | `easygit --private` |
| `--name` | `-n` | Specify repository name directly | `easygit --name "my-app"` |
| `--message` | `-m` | Specify initial commit message | `easygit -m "feat: first setup"` |
| `--dir` | `-d` | Target directory path | `easygit -d "D:\workspace\new-project"` |
| `--reset-token` | | Delete stored GitHub token | `easygit --reset-token` |

#### Examples:
```bash
# Initialize and push as private repository with custom commit message
easygit --private -m "Initial release"

# Target a specific directory and create as public
easygit -d "C:\temp\my-project" --name "my-service" --public
```

---

## 5. Troubleshooting (FAQ)

- **Q. How do I change or reset my GitHub token?**
  - Run `easygit --reset-token`. The stored token will be removed, and you will be prompted again on next run.
- **Q. What happens if a repository with the same name already exists on GitHub?**
  - EasyGit detects the conflict and asks whether you want to link and push to the existing repository (`y/N`).
- **Q. Will it fail if the folder is completely empty?**
  - No. If no trackable files are found, EasyGit automatically creates a default `README.md` with the project name before committing and pushing.

