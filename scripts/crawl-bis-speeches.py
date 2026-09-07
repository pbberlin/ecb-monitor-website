from pathlib import Path
import subprocess
import sys
from datetime import datetime

# compute paths only once
scriptDir = Path(__file__).resolve().parent
appDir    = scriptDir.parent
print(f"\t script     {Path(__file__).resolve()}   start")
print(f"\t scriptDir  {scriptDir} ")
print(f"\t appDir     {appDir} ")
bisDir    = appDir / "scripts" / "bis-speeches"


def runShellCommand(commandList, cwdPath: Path | None = None) -> int:
    try:
        result = subprocess.run(
            commandList,
            cwd=str(cwdPath) if cwdPath is not None else None,
            check=False
        )
        return result.returncode
    except Exception as exc:
        print(f"Exception while running command {commandList}: {exc}")
        return 1


def runBisPipeline() -> bool:

    # step 1
    cmd1 = [
        sys.executable, "crawl-01.py", 
        "--input",    "./ecb-members-input.csv", 
        "--output",   "./ecb-members-urls.csv", 
        "--headless", "true"
    ]
    if runShellCommand(cmd1, cwdPath=bisDir) != 0:
        return False

    # step 2
    cmd2 = [
        sys.executable, "crawl-02.py", 
        "--input",    "./ecb-members-urls.csv", 
        "--output",   "./ecb-members-links.csv", 
        "--headless", "true"
    ]
    if runShellCommand(cmd2, cwdPath=bisDir) != 0:
        return False

    # step 3 - takes ~20 min
    cmd3 = [
        sys.executable, "crawl-03.py", 
        "--input",     "./ecb-members-links.csv"
    ]
    if runShellCommand(cmd3, cwdPath=bisDir) != 0:
        return False

    # step 4
    cmd4 = [
        sys.executable, "crawl-04.py"
    ]
    if runShellCommand(cmd4, cwdPath=bisDir) != 0:
        return False

    # step 5 - OCR
    cmd5 = [
        sys.executable, "crawl-05-ocr.py"
    ]
    if runShellCommand(cmd5, cwdPath=bisDir) != 0:
        return False

    return True


def runGitRollback() -> None:
    try:
        # this will not remove newly created untracked files.
        runShellCommand(["git", "checkout", str(bisDir)], cwdPath=appDir)
    except Exception as exc:
        print(f"Exception while running git rollback: {exc}")


def runGitCommitPush() -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    import socket
    hostName = socket.gethostname()

    commitMessage = f"bis-speeches update {timestamp} {hostName}"

    runShellCommand(["git", "add", str(bisDir)], cwdPath=appDir)
    runShellCommand(["git", "commit", "-a", "-m", commitMessage], cwdPath=appDir)

    print("\tgit push start")
    runShellCommand(["git", "-c", "credential.helper=", "push"], cwdPath=appDir)
    print("\tgit push end")


def main() -> None:
    isSuccess = runBisPipeline()

    if isSuccess:
        print("bis pipeline succeeded - committing and pushing new data")
        runGitCommitPush()
    else:
        print("bis pipeline failed    - rolling back via git checkout")
        runGitRollback()


if __name__ == "__main__":
    main()