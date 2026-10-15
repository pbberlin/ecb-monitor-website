from pathlib import Path
import subprocess
import sys
import zipfile  # default module
from datetime import datetime

# resolving parent directory to import lib.util
parentDir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parentDir))
from lib.util import stackTrace


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
        stackTrace(exc)
        print(f"Exception while running command {commandList}")
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
        stackTrace(exc)
        print(f"Exception while running python script {scriptPath}")
        return 1


def runAmecoPipeline() -> bool:

    # ameco

    tmpZipPath = jobDirAmeco / "tmp-ameco-all.zip"

    curlCmd = [
        "curl",
        "https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco0_CSV.zip",
        "-o",
        str(tmpZipPath),
    ]
    if runShellCommand(curlCmd, cwdPath=appDir) != 0:
        return False


    fileList = ["AMECO6.CSV", "AMECO18.CSV", "AMECO16.CSV"]
    try:
        with zipfile.ZipFile(tmpZipPath, "r") as myZip:
            for idx1, myFile in enumerate(fileList):
                try:
                    myZip.extract(myFile, path=jobDirAmeco)
                except Exception as exFile:
                    stackTrace(exFile)
                    print(f"Exception extracting file {myFile}")
                    return False
    except Exception as exZip:
        stackTrace(exZip)
        print("Exception opening zip file")
        return False



    if runPythonScript(jobDirAmeco / "process-a-csv-to-subset.py", cwdPath=appDir) != 0:
        return False

    if runPythonScript(jobDirAmeco / "process-b-csv-to-js.py",     cwdPath=appDir) != 0:
        return False


    # eurostat

    eurostatTsv = jobDirEurostat / "estat_teimf050.tsv"
    downloadUrl = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/teimf050/?format=TSV&compressed=false"
    curlCmd = [
        "curl",
        downloadUrl,
        "-o",
        str(eurostatTsv),
        ]
    if runShellCommand(curlCmd, cwdPath=appDir) != 0:
        return False


    # 2026-10: new minr dataset
    eurostatTsv = jobDirEurostat / "estat_prc_hicp_minr.tsv"
    downloadUrl = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/prc_hicp_minr/1.0/*.*.*.*?c[freq]=M&c[unit]=RCH_A&c[coicop18]=TOTAL&compress=false&format=tsv"
    curlCmd = [
        "curl",
        downloadUrl,
        "-o",
        str(eurostatTsv),
        ]
    if runShellCommand(curlCmd, cwdPath=appDir) != 0:
        return False



    if runPythonScript(jobDirEurostat / "process-b-csv-to-js.py", cwdPath=appDir) != 0:
        return False






    #
    # ameco and eurostat


    # JS and CSV outputs are filtered
    if runPythonScript(scriptDir / "eu-and-euro-countries.py", cwdPath=scriptDir) != 0:
        return False


    if runPythonScript(scriptDir / "jsToCSV.py",         cwdPath=scriptDir) != 0:
        return False

    if runPythonScript(scriptDir / "validate-zabbix.py", cwdPath=scriptDir) != 0:
        return False

    return True


def runGitRollback() -> None:
    try:
        runShellCommand(["git", "checkout", str(dlDir)], cwdPath=appDir)
    except Exception as exc:
        stackTrace(exc)
        print("Exception while running git rollback")


def runGitCommitPush() -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    import socket
    hostName = socket.gethostname()

    commitMessage = f"ameco-eurostat update {timestamp} {hostName}"

    runShellCommand(["git", "add", str(dlDir)], cwdPath=appDir)
    runShellCommand(["git", "commit", "-a", "-m", commitMessage], cwdPath=appDir)

    #  no access to credential helper
    #  Jul 17 02:15:13 ecb-watch python[1946681]: Schwerwiegend: konnte Sperre für Zugangsdatenspeicher nicht in 1000 ms bekommen: Keine Berechtigung
    print("\tgit push start")
    runShellCommand(["git", "-c", "credential.helper=", "push"], cwdPath=appDir)
    print("\tgit push end")

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