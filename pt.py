class MutableAttribute:
    def __init__(self):
        self.parent = None

    def __set_name__(self, owner, name):
        self.name = f"_{name}"
        self.real_name = name

    def __get__(self, obj, objtype=None):
        if self.parent is None:
            self.parent = obj
        return getattr(obj, self.name)

    def __set__(self, obj, value):
        if self.parent is None:
            self.parent = obj
        processed_value = self.process(value)
        setattr(obj, self.name, processed_value)

    def process(self, value):
        print('Processing:', self.real_name, value)
        if hasattr(self.parent, 'process'):
            return self.parent.process(self.real_name, value)
        return value

class Test:
    page_id = MutableAttribute()
    count = MutableAttribute()

    def __init__(self):
        self.page_id = None
        self.count = 0

    def process(self, attr_name, value):
        print(f"Parent processing: {attr_name} = {value}")
        if attr_name == 'page_id':
            return str(value).strip()
        elif attr_name == 'count':
            return max(0, int(value))
        return value

# Example usage
if __name__ == "__main__":
    tt = Test()
    tt.page_id = '  105420925572228  '
    print(f"Stored page_id: {tt.page_id}")

    tt.count = "5"
    print(f"Stored count: {tt.count}")

    tt.count = -3
    print(f"Stored count after negative assignment: {tt.count}")