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
        raise FileNotFoundError(
            f"Source folder not found: {source}"
        )

    if not source.is_dir():
        raise NotADirectoryError(
            f"Source is not a folder: {source}"
        )

    backup_root.mkdir(parents=True, exist_ok=True)

    date_name = datetime.now().strftime("%Y-%m-%d")

    final_backup = backup_root / date_name
    incomplete_backup = backup_root / f".{date_name}.incomplete"

    # Remove an old incomplete backup before retrying.
    if incomplete_backup.exists():
        logging.warning(
            "RECOVERY | removing incomplete backup | path=%s",
            incomplete_backup,
        )
        shutil.rmtree(incomplete_backup)

    # Idempotency: do not create the same backup twice.
    if final_backup.exists():
        logging.info(
            "SKIPPED | backup already exists | path=%s",
            final_backup,
        )
        return "skipped"

    try:
        shutil.copytree(
            source,
            incomplete_backup,
        )

        incomplete_backup.rename(final_backup)

        logging.info(
            "SUCCESS | backup created | path=%s",
            final_backup,
        )

        return "success"

    except Exception:
        logging.exception(
            "FAILED | backup interrupted | path=%s",
            incomplete_backup,
        )
        raise


def main():
    config_path = Path("config.json")

    try:
        config = load_config(config_path)

        log_file = config.get(
            "log_file",
            "backup.log",
        )

        setup_logging(log_file)

        logging.info("START | backup run")

        result = create_backup(
            config["source"],
            config["backup_root"],
        )

        logging.info(
            "END | status=%s",
            result,
        )

    except Exception:
        logging.exception(
            "END | status=failed"
        )


if __name__ == "__main__":
    main()