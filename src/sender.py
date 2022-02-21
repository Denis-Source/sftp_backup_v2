import pysftp
import os
import time
import datetime

from config import Config
from src.file_tracker import FileTracker
from src.logger import Logger
from src.server_file import ServerFile
from src.client_file import ClientFile


class Sender:
    def __init__(self):
        self.file_tracker = FileTracker()
        self.connection = pysftp.Connection(
            username=Config.USERNAME,
            host=Config.HOST,
            private_key=Config.KEY_LOCATION
        )
        self.logger = Logger("sender")

    def validate_folder(self, folder_path):
        """
        Validates whether the folder is suitable for backup
        Filter is set in config as EXCLUDED_NAMES
        Cycles over the excluded names and checks
        if the name is suitable
        :param folder_path: str
        :return: bool
        """

        for name in Config.EXCLUDED_NAMES:
            if name in folder_path:
                self.logger.debug(f"folder with path {folder_path} skipped ({name} in path)")
                return False
        return True

    def validate_file(self, file_name):
        """
        Validates whether the file is suitable for backup
        Filter is set in config as EXCLUDED_FORMATS
        Cycles over the excluded file formats and checks
        if the file is suitable
        :param file_name: str
        :return: bool
        """
        for format_name in Config.EXCLUDED_FORMATS:
            if format_name in file_name:
                self.logger.debug(f"file with path {file_name} skipped ({format_name} format)")
                return False
        return True

    def add_server_file_stat(self, file_path):
        """
        Gets server file stats (such as last modified time for the specified file)
        Needed for recursive file walk in get_server_files()
        :param file_path: str
        :return: None
        """
        stat = self.connection.lstat(file_path)
        self.logger.debug(f"received stats for {file_path}")
        self.file_tracker.add_server_file(
            {
                file_path: ServerFile(file_path, stat.st_mtime)
            }
        )

    def add_server_folder(self, folder_path):
        self.file_tracker.add_server_folder(folder_path)

    def get_server_files(self):
        """
        Gets a list of all the server files in backup directories
        Checks directories specified in BACKUP_DIRECTORIES
        :return: None
        """
        self.logger.debug("Started scanning server files")
        for folder in Config.BACKUP_DIRECTORIES.values():
            self.logger.debug(f"Checking folder at {folder}")
            # The walktree() requires 3 callbacks as arguments
            # The first is used for a filepath and used for appending the server file list
            # The second is used for a dirpath and used for appending the server directory list
            # which is needed for empty folder clearing in the end of syncing
            # The third is for an unknown file type
            # Considering the third callback is not needed
            # dummy lambda function is used
            # hence the _ variables ¯\_(ツ)_/¯
            try:
                self.connection.walktree(
                    folder,
                    self.add_server_file_stat,
                    self.add_server_folder,
                    lambda _: _,
                )
            except FileNotFoundError:
                self.logger.debug(f"folder {folder} is not found")
        self.logger.info(f"total server files found: {ServerFile.total}")

    def get_client_files(self):
        """
        Gets all the files required to be backed up
        Cycles recursively over the directories specified in BACKUP_DIRECTORIES
        Validates folders and files
        If the file is suitable adds to the list
        :return: None
        """
        self.logger.debug("Started scanning client files")
        # 7 indentation in a row ¯\_(ツ)_/¯
        for folder in Config.BACKUP_DIRECTORIES:
            for (dir_path, dir_names, file_names) in os.walk(folder):
                if self.validate_folder(dir_path):
                    for file_name in file_names:
                        if self.validate_file(file_name):
                            self.logger.debug(f"found file {file_name} at {dir_path}")
                            file = ClientFile(
                                file_name,
                                dir_path,
                                folder,
                                Config.BACKUP_DIRECTORIES[folder]
                            )

                            self.file_tracker.add_client_file({
                                file.remote_path: file
                            })
        self.logger.info(f"total client files found: {ClientFile.total}")

    def sync_files(self):
        """
        Syncs files in specified folder in BACKUP_DIRECTORIES
        Gets a list of files to send/remove/update
        Sends required client files to a server files
        Removes redundant server files if they are not in client directory
        Updates outdated or recently changed files on server
        Detects empty folders and removes them
        :return:
        """

        started_time = time.time()

        # gets a list of files to delete form the server
        files_to_remove = self.file_tracker.get_files_to_remove()
        self.logger.info(f"total files to remove: {len(files_to_remove)}")
        for file in files_to_remove:
            self.connection.remove(file.remote_path)
            self.logger.info(f"removed remote file {file.remote_path}")

        # gets a list of files to send from the client
        files_to_send = self.file_tracker.get_files_to_send()
        self.logger.info(f"total files to send: {len(files_to_send)}")
        for file in files_to_send:
            # checks whether the folder exists
            # if not creates one
            try:
                self.connection.listdir(file.remote_dir)
                self.logger.debug(f"folder {file.remote_dir} already exists")
            except IOError:
                self.connection.makedirs(file.remote_dir)
                self.logger.info(f"created folder at {file.remote_dir}")
            self.connection.put(file.full_path, file.remote_path, preserve_mtime=True)
            self.logger.info(f"sent local file {file.full_path} to {file.remote_path}")

        # gets the list of files to update (remove and reupload)
        file_to_update = self.file_tracker.get_files_to_update()
        self.logger.info(f"total files to update: {len(file_to_update)}")
        for file in file_to_update:
            self.connection.put(file.full_path, file.remote_path, preserve_mtime=True)
            self.logger.debug(f"updated remote file {file.remote_path}")

        # gets the list of empty folders to remove them
        self.logger.debug("scanning for empty folders")
        current_dir = self.connection.pwd

        for folder in self.file_tracker.server_folders:
            to_remove = True
            for file in self.file_tracker.server_files:
                if folder in file:
                    to_remove = False
            if to_remove:
                self.logger.info(f"removing empty folder {folder}")
                # pysftp does not include a way
                # to remove a folder with its content
                # bash command to remove is rm {folder_path} -r
                # for reliability uses absolute path
                self.connection.execute(f"rm {current_dir}/{folder}/ -r")

        elapsed_time = round(time.time() - started_time)
        self.logger.info(f"backup finished! it took {datetime.timedelta(seconds=elapsed_time)}")

    def mainloop(self):
        """
        Main method
        Scans local files then server files and syncs them
        Sync is only one sided (from client to server)
        :return:
        """
        try:
            self.logger.info("backup started")
            self.get_client_files()
            self.get_server_files()
            self.sync_files()
        except Exception as e:
            self.logger.error(e)
