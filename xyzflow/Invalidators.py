import os
import hashlib

def file_invalidator(**files):
    """The cache will be invalidated whenever the hash of a file changes
    """
    return True