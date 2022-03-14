class Stack:
    def __init__(self):
        self.data = []
        self.size = 0

    def push(self, x):
        self.data.append(x)
        self.size += 1

    def pop(self):
        if self.size > 0:
            self.size -= 1
            return self.data.pop()
        else:
            return None

    def is_empty(self):
        return self.size == 0

    def peek(self):
        if self.size > 0:
            return self.data[self.size - 1]
        else:
            return None
