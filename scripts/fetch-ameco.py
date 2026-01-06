from pathlib import Path
import subprocess
import sys
import zipfile  # default module
from datetime import datetime


# compute paths only once
scriptDir = Path(__file__).resolve().parent
appDir    = scriptDir.parent
print(f"\t script     {Path(__file__).resolve()}   start")
print(f"\t scriptDir  {scriptDir} ")
print(f"\t appDir     {appDir} ")
jobDirAmeco     = appDir / "scripts" / "ameco"
jobDirEurostat  = appDir / "scripts" / "eurostat"
dlDir     = appDir / "static" / "dl"


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
    print(f"   workdir {cwdPath} ")
    print(f"   exec    {scriptPath}")
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

    # ameco

    tmpZipPath = jobDirAmeco / "tmp-ameco-all.zip"

    curlCmd1 = [
        "curl",
        "https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip",
        "-o",
        str(tmpZipPath),
    ]
    if runShellCommand(curlCmd1, cwdPath=appDir) != 0:
        return False


    fileList = ["AMECO18.CSV", "AMECO16.CSV"]
    try:
        with zipfile.ZipFile(tmpZipPath, "r") as myZip:
            for idx1, myFile in enumerate(fileList):
                try:
                    myZip.extract(myFile, path=jobDirAmeco)
                except Exception as exFile:
                    print(exFile)
                    return False
    except Exception as exZip:
        print(exZip)
        return False



    if runPythonScript(jobDirAmeco / "process-a-csv-to-subset.py", cwdPath=appDir) != 0:
        return False

    if runPythonScript(jobDirAmeco / "process-b-csv-to-js.py",     cwdPath=appDir) != 0:
        return False


    # eurostat

    amecoTsv = jobDirEurostat / "estat_teimf050.tsv"
    param2 = "curl \"https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/teimf050/?format=TSV&compressed=false\" -o estat_teimf050.tsv"
    param2 = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/teimf050/?format=TSV&compressed=false"
    curlCmd2 = [
        "curl",
        param2,
        "-o",
        str(amecoTsv),
    ]
    if runShellCommand(curlCmd2, cwdPath=appDir) != 0:
        return False


    if runPythonScript(jobDirEurostat / "process-b-csv-to-js.py", cwdPath=appDir) != 0:
        return False


    # ameco and eurostat

    if runPythonScript(dlDir / "jsToCSV.py",         cwdPath=dlDir) != 0:
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
