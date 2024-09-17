class Logger(object):
    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print('Creating new instance')
            cls._instance = cls.__new__(cls)
            # Put any initialization here.
        return cls._instance
    
log = Logger()
log1 = Logger.instance()
print(log1)
log2 = Logger.instance()
print(log2)
print('Are they the same object?', log1 is log2)
