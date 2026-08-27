def test_incomplete_backup_is_recovered(tmp_path):
    from datetime import datetime

    source = tmp_path / "source"
    backup_root = tmp_path / "backups"

    source.mkdir()
    backup_root.mkdir()

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