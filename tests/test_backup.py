import json
from datetime import datetime
from backup import create_backup, load_config


def test_load_config(tmp_path):
    config_file = tmp_path / "config.json"

    config_file.write_text(
        json.dumps({
            "source": "source",
            "backup_root": "backup",
            "log_file": "backup.log"
        }),
        encoding="utf-8"
    )

    config = load_config(config_file)

    assert config["source"] == "source"
    assert config["backup_root"] == "backup"
    assert config["log_file"] == "backup.log"


def test_backup_is_created(tmp_path):
    source = tmp_path / "source"
    backup_root = tmp_path / "backups"

    source.mkdir()
    (source / "file.txt").write_text(
        "hello",
        encoding="utf-8"
    )

    result = create_backup(source, backup_root)

    assert result == "success"

    date_name = datetime.now().strftime("%Y-%m-%d")
    backup_dir = backup_root / date_name

    assert backup_dir.exists()
    assert (backup_dir / "file.txt").exists()


def test_backup_is_idempotent(tmp_path):
    source = tmp_path / "source"
    backup_root = tmp_path / "backups"

    source.mkdir()
    (source / "file.txt").write_text(
        "hello",
        encoding="utf-8"
    )

    first = create_backup(source, backup_root)
    second = create_backup(source, backup_root)

    assert first == "success"
    assert second == "skipped"

    date_name = datetime.now().strftime("%Y-%m-%d")
    backup_dir = backup_root / date_name

    assert backup_dir.exists()


def test_missing_source_fails(tmp_path):
    source = tmp_path / "missing"
    backup_root = tmp_path / "backups"

    try:
        create_backup(source, backup_root)
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        assert True


def test_incomplete_backup_is_recovered(tmp_path):
    source = tmp_path / "source"
    backup_root = tmp_path / "backups"

    source.mkdir()
    backup_root.mkdir()

    (source / "new.txt").write_text(
        "new backup",
        encoding="utf-8"
    )

    result = create_backup(source, backup_root)

    assert result == "success"

    date_name = datetime.now().strftime("%Y-%m-%d")
    final_backup = backup_root / date_name

    assert final_backup.exists()
    assert (final_backup / "new.txt").exists()