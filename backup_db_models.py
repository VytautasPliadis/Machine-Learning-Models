#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import shutil

from src.utils.logger import logger

folder_to_backup = Path("model1")
backup_directory = Path("backups")
max_backups = 20


def create_backup(folder_path, backup_dir) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file_name = f"backup_{timestamp}.zip"
    backup_file_path = backup_dir / backup_file_name

    # Compress the folder
    shutil.make_archive(str(backup_file_path)[:-4], "zip", str(folder_path))
    logger.info(f"Backup created: {backup_file_path}")


def remove_old_backups(backup_dir, max_to_keep) -> None:
    backups = sorted(backup_dir.glob("*.zip"), key=lambda f: f.stat().st_ctime)

    while len(backups) > max_to_keep:
        backups[0].unlink()
        logger.info(f"Deleted old backup: {backups[0]}")
        backups.pop(0)


def main():
    create_backup(folder_to_backup, backup_directory)
    remove_old_backups(backup_directory, max_backups)


if __name__ == "__main__":
    main()
