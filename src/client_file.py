import os


class ClientFile:
    total = 0

    def __init__(self, name, folder, tracked_folder, remote_folder):
        self.name = name
        self.folder = folder
        self.tracked_folder = tracked_folder
        self.remote_folder = remote_folder
        self.full_path = os.path.join(folder, name)
        ClientFile.total += 1

    @property
    def last_modified(self):
        return round(os.path.getmtime(self.full_path) / 10) * 10

    @property
    def remote_path(self):
        rel_path = self.folder.replace(self.tracked_folder, "")
        return f"{self.remote_folder}/{rel_path}/{self.name}".replace("\\", "/").replace("//", "/")

    @property
    def remote_dir(self):
        rel_path = self.folder.replace(self.tracked_folder, "")
        return f"{self.remote_folder}/{rel_path}/".replace("\\", "/").replace("//", "/")

    def __eq__(self, other):
        return self.last_modified == other.last_modified

    def __hash__(self):
        return hash(self.remote_path)

    def __str__(self):
        return f"local {self.remote_path}\n" \
               f"mtime: {self.last_modified}"
