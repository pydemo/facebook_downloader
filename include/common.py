from collections import defaultdict


class PropertyDefaultDict(defaultdict):
    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__)
        if args:
            if isinstance(args[0], dict):
                for key, value in args[0].items():
                    self[key] = self.__class__(value) if isinstance(value, dict) else value
        self.update(kwargs)

    def __getattr__(self, key):
        if key.startswith('__') and key.endswith('__'):
            return super().__getattribute__(key)
        return self[key]

    def __setattr__(self, key, value):
        if key.startswith('__') and key.endswith('__'):
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __delattr__(self, key):
        if key.startswith('__') and key.endswith('__'):
            super().__delattr__(key)
        else:
            del self[key]

    def __repr__(self):
        return f"PropertyDefaultDict({dict.__repr__(self)})"

    def to_dict(self):
        return {k: v.to_dict() if isinstance(v, PropertyDefaultDict) else v for k, v in self.items()}


class CustomError(Exception):
    """Base class for custom exceptions in this module."""
    pass

class TokenExpiredError(CustomError):
    """Raised when page token is expired."""
    def __init__(self, r, json):
        self.value = r.status_code
        self.message = r.text
        self.json   = json
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}: {self.value}'
    
class ErrorValidatingAccessToken(CustomError):
    """Raised when page token is expired."""
  
    def __init__(self, r, json):
        if r:
            self.value = r.status_code
            self.message = r.text
        else:
            self.value = 0
            self.message = json
        self.json   = json
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}: {self.value}'
        



class VideoUploadIsMissingError(CustomError):
    """Raised when Video upload is missing ."""
    def __init__(self, r, json):
        self.value = r.status_code
        self.message = r.text
        self.json   = json
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}: {self.value}'
    