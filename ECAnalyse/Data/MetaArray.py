'''
This is a class for creating numpy array objects which can also carry metadata
which the user might not always want to access.
'''
import numpy as np
from numpy.lib import arraylike

class MetaArray(np.ndarray):
    def __new__(cls, data, **metadata):
        '''
        Create the array and assign the metadata
        '''
        obj = np.asarray(data).view(cls)
        for key, value in metadata.items():
            
            setattr(obj, key, value)
        return obj
    
    def __array_finalize__(self, obj):
        if obj is None: return
        # Copy over the metadata attributes
        for key in getattr(obj, '__dict__', {}):
            setattr(self, key, getattr(obj, key, None))