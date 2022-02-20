from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


class Config:
    HOST = "185.143.221.91"

    USERNAME = "den"
    KEY_LOCATION = r"C:\Keys\500rubles"

    BACKUP_DIRECTORIES = {r"C:\Shlack\kupyna": "kup"}
    EXCLUDED_NAMES = ["env", "venv", "."]
    EXCLUDED_FORMATS = ["pyc"]

    HISTORY_FILE = "files.dump"

    LOGGING_FILE = "sftp.log"

    LOGGING_COMMAND_LINE_LEVEL = DEBUG
    LOGGING_FILE_LEVEL = INFO
