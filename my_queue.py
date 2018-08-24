import codecs, os

class Queue:
    def __init__(self, file_path):
        self.queue = []
        self.file_path = file_path

    def merge(self, l):
        self.queue += l

    def insert(self, data):
        self.queue.append(data)
    
    def get_first(self):
        data = self.queue[0]
        self.queue = self.queue[1:]
        return data

    def save(self):
        with codecs.open(self.file_path, 'w', 'utf-8') as f:
            f.write('\n'.join(self.queue))

    def load(self):
        if os.path.isfile(self.file_path):
            with codecs.open(self.file_path, 'r', 'utf-8') as f:
                self.queue = f.read().split('\n')

    def length(self):
        return len(self.queue)

    def is_there(self, data):
        return data in self.queue

    def get_queue(self):
        return self.queue