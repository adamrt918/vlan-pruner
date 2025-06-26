class jsonDepth:
    def __init__(self):
        self.data = None

    def get_depth(self, data):
        start = data.find('{')
        if start == -1:
            return 0 # No JSON object found

        depth = 0
        for i in range(start, len(data)):
            if data[i] == '{':
                depth += 1
            elif data[i] == '}':
                depth -= 1
                if depth == 0:
                    return data[start:i+1]  # return full balanced block