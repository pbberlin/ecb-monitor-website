from pathlib import Path
import subprocess
import sys
from datetime import datetime


# compute paths only once
scriptDir = Path(__file__).resolve().parent
appDir = scriptDir.parent
jobDir = appDir / "scripts" / "ameco"
dlDir  = appDir / "static" / "dl"


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


def runPythonScript(scriptPath: Path, cwdPath: Path | None = None) -> int:
    try:
        result = subprocess.run(
            [sys.executable, str(scriptPath)],
            cwd=str(cwdPath) if cwdPath is not None else None,
            check=False
        )
        return result.returncode
    except Exception as exc:
        print(f"Exception while running python script {scriptPath}: {exc}")
        return 1


def runAmecoPipeline() -> bool:

    tmpZipPath = jobDir / "tmp-ameco-all.zip"

    curlCmd = [
        "curl",
        "https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip",
        "-o",
        str(tmpZipPath),
    ]
    if runShellCommand(curlCmd, cwdPath=appDir) != 0:
        return False

    tarCmd = [
        "tar",
        "-xf",
        str(tmpZipPath),
        "AMECO18.CSV",
        "AMECO16.CSV",
    ]
    if runShellCommand(tarCmd, cwdPath=appDir) != 0:
        return False

    if runPythonScript(jobDir / "process-a-csv-to-subset.py", cwdPath=appDir) != 0:
        return False

    if runPythonScript(jobDir / "process-b-csv-to-js.py", cwdPath=appDir) != 0:
        return False

    if runPythonScript(dlDir / "jsToCSV.py", cwdPath=dlDir) != 0:
        return False

    if runPythonScript(dlDir / "validate-zabbix.py", cwdPath=dlDir) != 0:
        return False

    return True


def runGitRollback() -> None:
    try:
        runShellCommand(["git", "checkout", str(dlDir)], cwdPath=appDir)
    except Exception as exc:
        print(f"Exception while running git rollback: {exc}")


def runGitCommitPush() -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commitMessage = f"ameco job success {timestamp}"

    runShellCommand(["git", "add", str(dlDir)], cwdPath=appDir)
    runShellCommand(["git", "commit", "-a", "-m", commitMessage], cwdPath=appDir)
    runShellCommand(["git", "push"], cwdPath=appDir)


def main() -> None:
    isSuccess = runAmecoPipeline()

    if isSuccess:
        print("ameco pipeline succeeded - committing and pushing new static/dl")
        runGitCommitPush()
    else:
        print("ameco pipeline failed    - rolling back static/dl via git checkout")
        runGitRollback()


if __name__ == "__main__":
    main()
