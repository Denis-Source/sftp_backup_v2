from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


class Config:
    # Credentials
    HOST = "ssh_ip"
    USERNAME = "ssh_username"
    KEY_LOCATION = r"key_path_location"

    # Backed up directories
    BACKUP_DIRECTORIES = {r"local_path1": "remote_folder1",
                          r"local_path2": "remote_folder2"}

    # Files and folders filtering
    EXCLUDED_NAMES = ["env", "venv", "."]
    EXCLUDED_FORMATS = ["pyc"]

    # Logging
    LOGGING_FILE = "sftp.log"
    LOGGING_COMMAND_LINE_LEVEL = INFO
    LOGGING_FILE_LEVEL = INFO
