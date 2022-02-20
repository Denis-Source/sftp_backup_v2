class FileTracker:
    def __init__(self):
        self.server_files = {}
        self.client_files = {}

    def add_server_file(self, file):
        """
        Adds the server file to a dictionary
        :param file: str
        :return: None
        """
        self.server_files.update(file)

    def add_client_file(self, file):
        """
        Adds the client file to a dictionary
        :param file: str
        :return: None
        """

        self.client_files.update(file)

    def get_files_to_send(self):
        """
        Gets the list of files that are missing
        and should be send to the server
        Uses set() difference method to get the required files
        :return: list
        """

        # Converting files (file paths as dictionary keys) to a set
        server_files = set(self.server_files)
        client_files = set(self.client_files)
        # Calculating difference and appending the list with the required files
        return [self.client_files[file] for file in client_files - server_files]

    def get_files_to_remove(self):
        """
        Gets the list of files that are redundant
        and should be deleted from the the server
        Uses the same principle as the previous method
        :return: list
        """

        server_files = set(self.server_files)
        client_files = set(self.client_files)
        return [self.server_files[file] for file in server_files - client_files]

    def get_files_to_update(self):
        """
        Gets the list of files that are modified
        since the last sending
        Checks last modified date of the client and server file
        Based on the __eq__() magic method
        of the ServerFile and Client file classes
        :return:
        """
        files = []
        # Cycles over all file paths in the list
        # Checks whether the file is already backed up
        for file_path in self.client_files:
            if file_path in self.server_files:
                if self.client_files[file_path] != self.server_files[file_path]:
                    files.append(self.client_files[file_path])
        return files

    def __str__(self):
        return f"Server Files:\n{self.server_files}\n\n" \
               f"Client Files:\n{self.client_files}"
