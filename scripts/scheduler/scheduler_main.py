from pathlib import Path
import subprocess
import sys
# pip install pyyaml
import yaml

# apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron       import CronTrigger


def loadJobConfig(configPath: Path) -> list:
    with configPath.open("r", encoding="utf-8") as configFile:
        configData = yaml.safe_load(configFile)

    jobs = configData.get("jobs", [])
    return jobs


def runScript(scriptPath: Path) -> None:
    try:
        subprocess.run(
            [sys.executable, str(scriptPath)],
            check=True
        )
    except Exception as exc:
        print(f"Error while running script {scriptPath}: {exc}")


def main() -> None:
    baseDir = Path(__file__).resolve().parent
    configPath = baseDir / "jobs_config.yaml"

    jobs = loadJobConfig(configPath)

    scheduler = BlockingScheduler()

    for idx1, jobConfig in enumerate(jobs):
        scriptRelPath = jobConfig["script"]
        cronExpr = jobConfig["cron"]
        jobId = jobConfig.get("id", f"job_{idx1}")

        scriptPath = baseDir / scriptRelPath

        trigger = CronTrigger.from_crontab(cronExpr)

        scheduler.add_job(
            runScript,
            trigger=trigger,
            id=jobId,
            args=[scriptPath]
        )

        print(f"Registered job {jobId} for script {scriptPath} with cron '{cronExpr}'")

    try:
        print("Starting scheduler...")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit) as exc:
        print(f"Scheduler stopped: {exc}")


if __name__ == "__main__":
    main()
