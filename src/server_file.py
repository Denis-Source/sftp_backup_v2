class ServerFile:
    total = 0

    def __init__(self, path, last_modified):
        self.remote_path = path
        self.last_modified = round(last_modified / 10) * 10
        ServerFile.total += 1

    def __eq__(self, other):
        return self.last_modified == other.last_modified

    def __hash__(self):
        return hash(self.remote_path)

    def __str__(self):
        return f"remote {self.remote_path}\n" \
               f"mtime: {self.last_modified}"
