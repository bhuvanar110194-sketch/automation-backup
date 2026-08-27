# Automation Script with Scheduling

A safe, unattended folder backup automation script written in Python.

## Features

- Scheduled recurring backups
- Idempotent execution
- Structured logging
- Configuration stored outside the code
- Secrets kept outside the repository
- Partial failure handling
- Recovery from interrupted backups
- Safe to run multiple times

## Project Structure

automation-backup/
├── backup.py
├── config.example.json
├── README.md
├── sample.log
├── .gitignore
└── tests/
    └── test_backup.py

## Configuration

Create a local `config.json` from `config.example.json`.

Example:

{
  "source": "/path/to/source-folder",
  "backup_root": "/path/to/backup-folder",
  "log_file": "backup.log"
}

Do not commit `config.json`.

## Idempotency

The script creates one backup per day.

If the backup for the current date already exists, another backup is not created.

This makes it safe to run the script multiple times.

## Logging

Each run records:

- Start of the run
- Backup status
- Backup location
- Errors and exceptions

Example log:

2026-08-27 09:30:00 | INFO | START | backup run
2026-08-27 09:30:02 | INFO | SUCCESS | backup created | path=/backup/2026-08-27
2026-08-27 09:30:02 | INFO | END | status=success

A second run on the same day:

2026-08-27 10:00:00 | INFO | START | backup run
2026-08-27 10:00:00 | INFO | SKIPPED | backup already exists | path=/backup/2026-08-27
2026-08-27 10:00:00 | INFO | END | status=skipped

## Partial Failure Recovery

Backups are first copied into a temporary `.incomplete` directory.

Only after the copy completes successfully is the directory renamed to the final backup directory.

If a run fails halfway:

1. The log records the failure.
2. The incomplete directory identifies the interrupted backup.
3. The next run removes the incomplete directory.
4. A fresh backup is created.
5. The final backup directory is only created after a successful copy.

This prevents an incomplete backup from being treated as a successful backup.

## Scheduling

The script can be scheduled using:

- Windows Task Scheduler
- Linux/macOS cron
- CI/CD scheduled jobs

Example cron schedule for running daily at 2:00 AM:

0 2 * * * python /path/to/backup.py

## Security

Real configuration files, logs and secrets are excluded using `.gitignore`.

Never store passwords, API keys or other secrets in the source code or Git repository.

## Testing

Run:

pytest

The tests verify idempotency, successful backup creation and failure handling.
