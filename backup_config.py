"""
General Python3 script for IP Fabric's API to download the latest available configuration files.

2023-02 - Version 1.0
using ipfabric SDK
WARNING: you should make sure the SDK version matches your version of IP Fabric

"""
# Built-in/Generic Imports
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path, PosixPath

import typer
from dotenv import load_dotenv
from ipfabric import IPFClient
from ipfabric.tools import DeviceConfigs
from loguru import logger


# Variable inputs
CURRENT_FOLDER = Path(os.path.realpath(os.path.dirname(sys.argv[0]))).resolve()
DEFAULT_BACKUP_FOLDER = CURRENT_FOLDER / "backup"
# Log variables
LOG_FILE = CURRENT_FOLDER / "logs/backup_config.log"
LOGGER_DEBUG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <yellow><italic>{elapsed}</italic></yellow> | <level>{level: <8}</level> | <level>{message}</level>"
LOGGER_INFO_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <yellow><italic>{elapsed}</italic></yellow> | <level>{message}</level>"
# Load variables from .env
load_dotenv(os.path.join(CURRENT_FOLDER, ".env"), override=True)

app = typer.Typer(add_completion=False)


def valid_json(raw_data: str):
    """
    Confirm the raw data is a valid JSON. Return the json if OK, or exit.
    """
    try:
        json_data = json.loads(raw_data)
    except json.JSONDecodeError as exc:
        print(f"##ERR## The filter is not a valid JSON format: {exc}\n'{raw_data}'")
        sys.exit()
    return json_data


def initiate_destination_folder(destination_folder: PosixPath, git_disabled: bool):
    """
    Function to check or create the destination folder
    and enable git if the option is activated
    """
    git_folder = destination_folder / ".git"
    if not destination_folder.is_dir():
        destination_folder.mkdir()
        logger.info(f"Directory `{destination_folder}` has been created")
    if not git_disabled and not git_folder.is_dir():
        subprocess.call(["git", "init"], cwd=destination_folder)
        logger.info("<GIT>: git has been initiated")


def create_config_file(device_config: object, device: list, destination_folder: str):
    """
    Function to write the config file to the Destination folder
    """
    # Define the file path where you want to save the file
    file_path = (
        destination_folder
        / f"{device['hostname'].replace('/','-')}--{device['sn'].replace('/','-')}.txt"
    )

    # Write the text to the file
    with open(file_path, "w") as f:
        f.write(device_config.text)


@app.command()
def main(
    folder=typer.Option(
        DEFAULT_BACKUP_FOLDER, "-f", "--folder", help="Select the backup folder."
    ),
    git_disabled: bool = typer.Option(
        False, "--no-git", "-ng", help="Disable GIT option for the Backup folder."
    ),
    sanitized: bool = typer.Option(
        False,
        "--sanitized",
        "-s",
        help="Sanitized configuration by removing some data.",
    ),
):
    """
    Main function
    - initiate the logger
    - initiate the IPF client and the destination folder
    - For each device of the (filtered) inventory, download the IPF config based
    - Write the fileto disk
    - (Optional) Use git on the destination folder to track changes
    """
    # PRD mode, we don't show diagnose to avoid leaking info to the logs.
    # logger.add(
    #     sys.stderr,
    #     colorize=True,
    #     level="INFO",
    #     format=LOGGER_INFO_FORMAT,
    #     diagnose=False,
    # )
    logger.add(
        LOG_FILE,
        colorize=True,
        level="INFO",
        format=LOGGER_DEBUG_FORMAT,
        diagnose=False,
        rotation="1 MB",
        compression="bz2",
        retention="2 months",
    )
    logger.info("------------- STARTING SCRIPT -------------")
    # Getting data from IP Fabric and printing output
    ipf_client = IPFClient(
        base_url=os.getenv("IPF_URL"),
        token=os.getenv("IPF_TOKEN"),
        snapshot_id=os.getenv("IPF_SNAPSHOT", "$last"),
        verify=(os.getenv("IPF_VERIFY", "False") == "True"),
    )
    destination_folder = Path(folder)
    initiate_destination_folder(destination_folder, git_disabled)

    # Select only the specified hostnames based on the filter
    inventory_filter = valid_json(os.getenv("INVENTORY_FILTER", "{}"))
    input_devices_sn = [
        {"sn": host["sn"], "hostname": host["hostname"]}
        for host in ipf_client.inventory.devices.all(filters=inventory_filter)
    ]
    # Get and write the config from IP Fabric
    config = DeviceConfigs(ipf_client)
    for device in input_devices_sn:
        if device_config := config.get_configuration(
            sn=device["sn"], sanitized=sanitized
        ):
            # copy the text file to somewhere \\\69212163
            logger.info(f"{device['hostname']} - copy the configuration")
            create_config_file(device_config, device, destination_folder)
        else:
            logger.info(f"{device['hostname']} - no config file found in IPF")

    if not git_disabled:
        # Create the commit message with the current date and time
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M")
        subprocess.call(["git", "add", "-A"], cwd=destination_folder)
        git_commit = subprocess.run(
            ["git", "commit", "-m", f"Backup {date_time}"],
            cwd=destination_folder,
            capture_output=True,
            check=False,
        )
        if "\\nnothing to commit" in str(git_commit.stdout):
            logger.info("<GIT>: No change to commit")
        else:
            logger.info(f"<GIT>: git commit: {str(git_commit.stdout)}")
    else:
        logger.info("<GIT>: Git Option not activated")
    logger.info("-------------- END OF SCRIPT --------------")


if __name__ == "__main__":
    app()
