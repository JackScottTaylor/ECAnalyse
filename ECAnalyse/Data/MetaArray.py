'''
This is a really useful object when it would be good for a function to return 
a numpy array but sometimes extra data may be required.

For example:
capacitances = gcd.capacitances()
Then most cases you would just want to treat capacitances as a numpy array but
now that is possible as well as also being able to access the calculated errors 
as capacitances.errors.

Note that performing any operation on the MetaArray removes the metadata from 
the resultant array which is type numpy.NDArray
'''
import numpy as np

class MetaArray(np.ndarray):
    def __new__(cls, input_array, **metadata):
        obj = np.asarray(input_array).view(cls)
        obj._metadata = metadata
        for key, value in metadata.items():
            setattr(obj, key, value)
        return obj

    def __array_finalize__(self, obj):
        # Called on new views or slices
        if obj is None: return
        metadata = getattr(obj, '_metadata', {})
        self._metadata = metadata
        for key, value in metadata.items():
            setattr(self, key, value)

    def __array_wrap__(self, out_arr, context=None, return_scalar=None):
        # This is called after ufuncs and similar operations.
        # Returning a base ndarray will drop the subclass and metadata.
        return np.asarray(out_arr)  # convert to plain ndarray, metadata lost

    def __repr__(self):
        base = super().__repr__()
        meta_str = ", ".join(f"{k}={v}" for k, v in self._metadata.items())
        return f"{base}\nMeta: {{{meta_str}}}"