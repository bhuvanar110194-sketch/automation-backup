import json
import logging
import shutil
from datetime import datetime
from pathlib import Path


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def create_backup(source, backup_root):
    source = Path(source)
    backup_root = Path(backup_root)

    if not source.exists():
        raise FileNotFoundError(f"Source folder not found: {source}")

    if not source.is_dir():
        raise NotADirectoryError(f"Source is not a folder: {source}")

    backup_root.mkdir(parents=True, exist_ok=True)

    date_name = datetime.now().strftime("%Y-%m-%d")
    backup_dir = backup_root / date_name

    if backup_dir.exists():
        logging.info(
            "SKIPPED | backup already exists | path=%s",
            backup_dir,
        )
        return "skipped"

    temp_dir = backup_root / f".{date_name}.incomplete"

    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

        shutil.copytree(source, temp_dir)
        temp_dir.rename(backup_dir)

        logging.info(
            "SUCCESS | backup created | path=%s",
            backup_dir,
        )

        return "success"

    except Exception:
        logging.exception(
            "FAILED | backup interrupted | temp=%s",
            temp_dir,
        )
        raise


def main():
    config_path = Path("config.json")

    try:
        config = load_config(config_path)

        log_file = config.get("log_file", "backup.log")
        setup_logging(log_file)

        logging.info("START | backup run")

        result = create_backup(
            config["source"],
            config["backup_root"],
        )

        logging.info("END | status=%s", result)

    except Exception:
        logging.exception("END | status=failed")


if __name__ == "__main__":
    main()
