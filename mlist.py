from pubsub import pub

class MutableList(list):
    def __init__(self, parent_obj, descriptor):
        super().__init__(getattr(parent_obj, descriptor.name))
        self.parent_obj = parent_obj
        self.descriptor = descriptor

    def add_item(self, item):
        if not isinstance(item, dict):
            raise ValueError("Item must be a dictionary")
        self.append(item)
        self.descriptor.__set__(self.parent_obj, self)

    def remove_item(self, index):
        if 0 <= index < len(self):
            del self[index]
            self.descriptor.__set__(self.parent_obj, self)
        else:
            raise IndexError("Index out of range")

    def update_item(self, index, new_item):
        if not isinstance(new_item, dict):
            raise ValueError("New item must be a dictionary")
        if 0 <= index < len(self):
            self[index] = new_item
            self.descriptor.__set__(self.parent_obj, self)
        else:
            raise IndexError("Index out of range")
        
class MutableListAttribute:
    def __init__(self):
        self.parent = None
        self.name = None
        self.real_name = None

    def __set_name__(self, owner, name):
        self.name = f"_{name}"
        self.real_name = name

    def __get__(self, obj, objtype=None):
        if self.parent is None:
            self.parent = obj
        if not hasattr(obj, self.name):
            setattr(obj, self.name, [])
        return MutableList(obj, self)

    def __set__(self, obj, value):
        if not isinstance(value, list):
            raise ValueError("Value must be a list")
        if not all(isinstance(item, dict) for item in value):
            raise ValueError("All items in the list must be dictionaries")
        if self.parent is None:
            self.parent = obj
        processed_value = self.process(value)
        setattr(obj, self.name, processed_value)
        self.notify_change(processed_value)

    def process(self, value):
        print(f'Processing: {self.real_name}', value)
        if hasattr(self.parent, 'process'):
            return self.parent.process(self.real_name, value)
        return value

    def notify_change(self, value):
        pub.sendMessage(f'{self.real_name}_changed', value=value)



# Example usage class
class MyClass:
    my_list = MutableListAttribute()

    def process(self, name, value):
        print(f"Custom processing in MyClass: {name}")
        return value

    def on_my_list_changed(self, value):
        print(f"my_list changed: {value}")

# Usage example
if __name__ == "__main__":
    # Subscribe to the change notification
    pub.subscribe(MyClass().on_my_list_changed, "my_list_changed")

    # Create an instance of MyClass
    obj = MyClass()

    # Set initial list
    obj.my_list = [{"key": "value"}]

    # Add a new item
    obj.my_list.add_item({"new_key": "new_value"})

    # Update an item
    obj.my_list.update_item(0, {"updated_key": "updated_value"})

    # Remove an item
    obj.my_list.remove_item(1)

    # Use as a regular list
    obj.my_list.append({"another_key": "another_value"})

    # Access items directly
    print("First item:", obj.my_list[0])

    # Print the entire list
    print("Final list:", obj.my_list)