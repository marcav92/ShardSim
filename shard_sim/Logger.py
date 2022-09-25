class Logger:

    def __init__(self, file_name, filters):
        self.file_name = file_name
        self.filters = filters
        self.count = 0

    

    def create_file(self):
        f = open(self.file_name, "w")
        f.write("=================================================")
        f.write("Sharsim log start")
        f.write("=================================================")
        f.close()

    def append_log(self, event):
        if self.filters:
            if event.data["type"] in self.filters:
                self.count += 1
                f = open(self.file_name, "a")
                f.write(f"{self.count}:"+str(event))
                f.close()

        else:
            self.count += 1
            f = open(self.file_name, "a")
            f.write(f"{self.count}:"+str(event))
            f.close()