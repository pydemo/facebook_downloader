import  sys, json, codecs
import re
from pubsub import pub
from pprint import pprint as pp
from include.common import PropertyDefaultDict
from pubsub import pub
from datetime import date
from os.path import join    

from os.path import isfile


e=sys.exit
class MutableAttribute:
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
        return getattr(obj, self.name, None)

    def __set__(self, obj, value):
        if self.parent is None:
            self.parent = obj
        processed_value = self.process(value)
        setattr(obj, self.name, processed_value)
        self.notify_change(processed_value)

    def process(self, value):
        print('777 Processing:', self.real_name, value)
        if hasattr(self.parent, 'process'):
            return self.parent.process(self.real_name, value)
        return value

    def notify_change(self, value):
        pub.sendMessage(f'{self.real_name}_changed', value=value)
        print('888 Notifying:', self.real_name, value)
        #pub.sendMessage('{self.real_name}_changed', name=self.real_name, value=value)





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
        
        return getattr(obj, self.name, None)

    def __set__(self, obj, value):
        if self.parent is None:
            self.parent = obj
        processed_value = self.process(value)
        if isinstance(processed_value, dict):
            processed_value = NotifyingDict(processed_value, parent=self, key=self.real_name)
        setattr(obj, self.name, processed_value)
        

    def process(self, value):
        print('222 Processing:', self.real_name, value)
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
         
        #pub.sendMessage(f'{attr_name}_changed', value=value)



class DictWithAttributes:
    page_info = MutableDictAttribute()

    def __init__(self):
        dt = date.today().strftime("%Y-%m-%d")
        self.page_info[dt] = {'followers': 0, 'delta': 0}

    def process(self, attr_name, value):
        print(f'-----parent Processing: {attr_name} {value} {type(value)}')
        if  isinstance(value, dict):
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

if 0:
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
    e()

if 0:
    class DictWithAttributes:
        page_info = MutableDictAttribute()
        def __init__(self) -> None:
            from datetime import date
            dt = date.today().strftime("%Y-%m-%d")
            # Using attribute syntax with nested dictionaries
            self.page_info = {dt:{'followers':0, 'delta':0}}
            

            
            
            print("\nAccessing nested values:")
            print(f"Page ID: {self.page_info[dt]}")
            
            self.page_info[dt]['followers']=5
            print(f"Page ID: {self.page_info[dt]}")
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

    # Example usage
    if 1:
        

        data = DictWithAttributes()
        if 1:
            from datetime import date
            dt = date.today().strftime("%Y-%m-%d")
            
            # Using attribute syntax with nested dictionaries
            data.page_info = {dt: {'followers': 0, 'delta': 0}}
            
            print("\nAccessing nested values:")
            print(f"Page ID: {data.page_info[dt]}")
            
            # Using attribute access
            data.page_info[dt].followers = 5
            print(f"Page ID: {data.page_info[dt]}")
            
            # Demonstrating attribute access
            print(f"Followers: {data.page_info[dt].followers}")
            print(f"Delta: {data.page_info[dt].delta}")        

        e()  


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
        #print(f'Processing: {self.real_name}', value)
        if hasattr(self.parent, 'process'):
            return self.parent.process(self.real_name, value)
        return value

    def notify_change(self, value):
        pub.sendMessage(f'{self.real_name}_changed', value=value)


class Config(): 
    user = MutableAttribute()
    page_id = MutableAttribute()
    reel_id = MutableAttribute()
    user_token = MutableAttribute()
    scope_rowid = MutableAttribute()
    input_files = MutableDictAttribute()
    scope_name = MutableAttribute()
    
    followers_count = MutableDictAttribute()
    num_of_uploads = MutableDictAttribute()
    user_tokens = MutableDictAttribute()    
    uloaded_cnt = MutableAttribute()
    page_tokens = MutableDictAttribute()  
    all_reel_descr = MutableDictAttribute()  
    scope_log = MutableListAttribute()
    upload_log = MutableDictAttribute()
    
    scopes = MutableDictAttribute()
    def __init__(self, **kwargs):
        self.cfg={}
 
        self.home=None
        #self.page_tokens_fn='.page_tokens.json'
        self.dump_file={}
        
        self.mta=set()
        self.page_id = self.get_attr('page_id')
        self.reel_id = self.get_attr('reel_id')
        self.scope_rowid = self.get_attr('scope_rowid')
        self.input_files = self.get_attr('input_files')
        self.scope_name = self.get_attr('scope_name','default')
        

        self.users=self.get_attr('users', {}, '.init.json')
        assert self.users, 'No users defined in config'
        default_user=self.get_attr('default_user', None, '.init.json')
        assert default_user
        self.user=self.get_attr('user',default_user)
        self.user_tokens = self.get_attr('user_tokens',{user:'' for user in self.users})
        self.user_token=self.get_user_token()
        self.page_id= self.get_attr('page_id','105420925572228')
        self.all_reel_descr = self.get_attr('all_reel_descr',{self.user:{self.page_id:'💙💛#StandWithUkraine💙💛'}})
        
        self.uploaded_cnt = self.get_attr('uploaded_cnt')
        from datetime import date
        self.dt=dt = date.today().strftime("%Y-%m-%d")   

        self.upload_log = self.get_attr(f'{dt}_upload_log', {})
        self.scopes=self.get_attr('scopes', {}, join('config', 'scopes.json'))  


        self.scope_log = self.get_attr('scope_log', [], '.scope_log.json')
        self.task_log = self.get_attr('task_log', [], '.task_log.json')
        self.num_of_uploads = self.get_attr('num_of_uploads') #self.get_attr('followers_count',{dt:dict(followers=0, delta=0)})
        #dtc= self.followers_count.get(dt)
        if not self.num_of_uploads or not  self.num_of_uploads.get(self.page_id):
            self.num_of_uploads={self.user:{self.page_id:{dt:{'uploads':0}}}}

        self.page_tokens = self.get_attr('page_tokens',{user:PropertyDefaultDict() for user in self.users}, '.page_tokens.json')
        self.pages=self.page_tokens[self.user]
        
        self.followers_count = self.get_attr('followers_count') #self.get_attr('followers_count',{dt:dict(followers=0, delta=0)})
        #dtc= self.followers_count.get(dt)
        if not self.followers_count or not  self.followers_count.get(self.page_id):
            self.followers_count={self.user:{self.page_id:{dt:{'followers':0, 'delta':0, 'increment':0}}}}
        
        #print(777,self.followers_count, type(self.followers_count))
        #print(999, type(self.followers_count))
        #self.followers_count[dt]['followers']   =5
        
        if 0 and self.page_id:
            print('Page ID:', self.page_id)
            self.init_pages()
    def get_reel_descr(self):
        print   ('-----Getting reel descr:', self.user, self.page_id)
        return self.all_reel_descr[self.user].get(self.page_id,'No description')
    def set_reel_descr(self, descr):
        print('Setting reel descr:', descr) 
        self.all_reel_descr[self.user][self.page_id] = descr
            
    def get_user_token(self):
        user_token=self.user_tokens[self.user]
        if user_token:
            return user_token   
        else:
            return ''
    def set_user_token(self, user_token):
        self.user_token = user_token
        self.user_tokens[self.user] = user_token
        
    def increment_uploads(self):

        self.num_of_uploads[self.user][self.page_id][self.dt]['uploads'] += 1
        
    def get_attr(self, attr, default=None, dump_file='.config.json'): 
        if attr not in self.dump_file:
            self.dump_file[attr]=dump_file
        config_fn=self.dump_file[attr]
        self.mta.add(attr)
        print('-------------------config_fn: ' , attr, config_fn)
        if config_fn not in self.cfg:
            self.cfg[config_fn]={}
        cfg=self.cfg[config_fn]

        if not cfg:
            if isfile(config_fn):
                try:
                    print(f"Reading config file {config_fn}")
                    with open(config_fn, 'r') as f:
                        content = f.read().strip()
                        #pp(content)
                        if content:
                            cfg_dump = json.loads(content)
                            #pp(cfg_dump)
                            self.cfg[config_fn]=cfg=cfg_dump
                        else:
                            print(f"Warning: {config_fn} is empty.")
                except json.JSONDecodeError as e:
                    print(f"Error reading config file {config_fn}: {e}")
                    #print("Initializing with an empty PropertyDefaultDict.")
                except Exception as e:
                    print(f"Unexpected error reading config file {config_fn}: {e}")
                    #print("Initializing with an empty PropertyDefaultDict.")
            else:
                print(f"Warning: connfig file {config_fn} does not exist.")
            
                
        if cfg:
            print(8888, cfg)
            #print (attr.name)
            value=cfg.get(attr, default)
            print('Getting:', attr, type(value))   
           
            
            return value
        self.cfg[config_fn]=cfg
        return default
    def set_attr(self, attr, value):
        #print('Setting:', attr, value, type(value))
        assert attr in self.dump_file, f'set_attr: No dump file specified for attr "{attr}"'
        dump_file = self.dump_file[attr]   
        assert dump_file, f'set_attr: dump_file is not set  for attr "{attr}"'     
        cfg=self.cfg[dump_file]
        #pp(self.cfg)
        assert cfg is not None, dump_file
        cfg[attr]=value

        assert dump_file, 'set_attr: No dump file specified'
        print('Dumping ******************************:', attr, dump_file)    
        with open(dump_file, 'w') as f:
            json.dump(cfg, f, indent=2)
        
        
    def process(self, attr_name, value):
        #print   ('-----Processing:', attr_name, value)
        if attr_name in self.mta: # ['page_id', 'reel_id', 'user_token','followers_count','uploaded_cnt']:
            #print(f"Parent processing: {attr_name} = {value}")
            if value:
                self.set_attr(attr_name, value)
            return value
        
        return value  
    def _process_dict(self, attr_name, value):
        #print   ('-----Processing dict:', attr_name, value)
        if attr_name in ['followers_count']:
            print(f"Parent dict processing: {attr_name} = {value}")
            if value:
                self.set_attr(attr_name, value)
            return str(value).strip()
        
        
        return value 
    

    def _process(self, attr_name, value):
        #print(f'-----parent Processing: {attr_name} {value} {type(value)}')
        if attr_name in self.mta:        
            if  isinstance(value, dict):
                self.process_dict(value)
            return value

    def _process_dict(self, d):
        for key, value in d.items():
            if isinstance(value, str):
                d[key] = value.strip()
            elif isinstance(value, dict):
                self.process_dict(value)

    def _load_page_tokens(self):
        if not self.pages:
            self.pages = self.init_pages()
        return self.pages              
    def _dump_page_tokens(self):
        with open(self.page_tokens_fn, 'w') as f:
            #pp(self.pages.to_dict())
            json.dump(self.pages, f, indent=2)
    def _init_pages(self):
        self.pages = PropertyDefaultDict()
        if isfile(self.page_tokens_fn):
            try:
                print(f"Reading page tokens from {self.page_tokens_fn}")
                with open(self.page_tokens_fn, 'r') as f:
                    content = f.read().strip()
                    if content:
                        js = json.loads(content)
                        self.pages = PropertyDefaultDict(js)
                    else:
                        print(f"Warning: {self.page_tokens_fn} is empty.")
            except json.JSONDecodeError as e:
                print(f"Error reading {self.page_tokens_fn}: {e}")
                print("Initializing with an empty PropertyDefaultDict.")
            except Exception as e:
                print(f"Unexpected error reading {self.page_tokens_fn}: {e}")
                print("Initializing with an empty PropertyDefaultDict.")
        else:
            print(f"Warning: {self.page_tokens_fn} does not exist.")

        return self.pages
