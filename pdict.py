from pubsub import pub
from datetime import date

class NotifyingDict(dict):
    def __init__(self, *args, parent=None, key=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.key = key
        self._processing = False
        for k, v in self.items():
            if isinstance(v, dict):
                self[k] = NotifyingDict(v, parent=self, key=k)

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, NotifyingDict):
            value = NotifyingDict(value, parent=self, key=key)
        super().__setitem__(key, value)
        self.propagate_change()

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'NotifyingDict' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in ['parent', 'key', '_processing']:
            super().__setattr__(name, value)
        else:
            self[name] = value

    def propagate_change(self):
        if self.parent and not self._processing:
            if isinstance(self.parent, NotifyingDict):
                self.parent.propagate_change()
            elif isinstance(self.parent, MutableDictAttribute):
                self.parent.child_changed()
        pub.sendMessage('dict_changed', key=self.key, value=self)

class MutableDictAttribute:
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
        value = getattr(obj, self.name, None)
        if value is None:
            value = NotifyingDict(parent=self, key=self.real_name)
            setattr(obj, self.name, value)
        return value

    def __set__(self, obj, value):
        if self.parent is None:
            self.parent = obj
        processed_value = self.process(value)
        if isinstance(processed_value, dict) and not isinstance(processed_value, NotifyingDict):
            processed_value = NotifyingDict(processed_value, parent=self, key=self.real_name)
        setattr(obj, self.name, processed_value)
        pub.sendMessage(f'{self.real_name}_changed', value=processed_value)

    def process(self, value):
        print('Processing:', self.real_name, value)
        if hasattr(self.parent, 'process'):
            return self.parent.process(self.real_name, value)
        return value

    def child_changed(self):
        if hasattr(self.parent, 'process'):
            current_value = getattr(self.parent, self.name, None)
            if current_value is not None:
                current_value._processing = True
                processed = self.parent.process(self.real_name, current_value)
                current_value._processing = False
                setattr(self.parent, self.name, processed)
        pub.sendMessage(f'{self.real_name}_changed', value=getattr(self.parent, self.name))

class DictWithAttributes:
    page_info = MutableDictAttribute()

    def __init__(self):
        dt = date.today().strftime("%Y-%m-%d")
        self.page_info[dt] = {'followers': 0, 'delta': 0}

    def process(self, attr_name, value):
        print(f'-----parent Processing: {attr_name} {value} {type(value)}')
        if attr_name == 'page_info' and isinstance(value, dict):
            self.process_dict(value)
        return value

    def process_dict(self, d):
        for key, value in d.items():
            if isinstance(value, str):
                d[key] = value.strip()
            elif isinstance(value, dict):
                self.process_dict(value)

# Example usage and testing
def on_dict_changed(key, value):
    print(f"Dict changed: {key} = {value}")

def on_page_info_changed(value):
    print(f"page_info changed: {value}")

if __name__ == "__main__":
    pub.subscribe(on_dict_changed, 'dict_changed')
    pub.subscribe(on_page_info_changed, 'page_info_changed')

    data = DictWithAttributes()
    dt = date.today().strftime("%Y-%m-%d")

    print("\nChanging followers:")
    data.page_info[dt]['followers'] = 5
    
    print("\nChanging delta:")
    data.page_info[dt]['delta'] = 2

    print("\nAdding new date:")
    new_dt = "2024-08-29"
    data.page_info[new_dt] = {'followers': 10, 'delta': 5}

    print("\nAccessing values:")
    print(f"Followers: {data.page_info[dt]['followers']}")
    print(f"Delta: {data.page_info[dt]['delta']}")
    print(f"New date followers: {data.page_info[new_dt]['followers']}")