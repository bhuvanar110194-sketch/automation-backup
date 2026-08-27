import json

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


def test_backup_is_created(tmp_path):
    source = tmp_path / "source"
    backup_root = tmp_path / "backups"

    source.mkdir()
    (source / "file.txt").write_text("hello", encoding="utf-8")

    result = create_backup(source, backup_root)

    assert result == "success"

    backup_dirs = list(backup_root.iterdir())
    assert len(backup_dirs) == 1

    assert (backup_dirs[0] / "file.txt").read_text(
        encoding="utf-8"
    ) == "hello"


def test_backup_is_idempotent(tmp_path):
    source = tmp_path / "source"
    backup_root = tmp_path / "backups"

    source.mkdir()
    (source / "file.txt").write_text("hello", encoding="utf-8")

    first = create_backup(source, backup_root)
    second = create_backup(source, backup_root)

    assert first == "success"
    assert second == "skipped"

    backups = list(backup_root.iterdir())
    assert len(backups) == 1


def test_missing_source_fails(tmp_path):
    source = tmp_path / "missing"
    backup_root = tmp_path / "backups"

    try:
        create_backup(source, backup_root)
        assert False
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

    from datetime import datetime

    date_name = datetime.now().strftime("%Y-%m-%d")
    incomplete = backup_root / f".{date_name}.incomplete"

    incomplete.mkdir()
    (incomplete / "old.txt").write_text(
        "partial",
        encoding="utf-8"
    )

    result = create_backup(source, backup_root)

    assert result == "success"
    assert not incomplete.exists()

    final_backup = backup_root / date_name

    assert final_backup.exists()
    assert (final_backup / "new.txt").exists()