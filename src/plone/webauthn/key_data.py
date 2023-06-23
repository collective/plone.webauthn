import zope.interface
from zope.annotation.interfaces import IAnnotations
from BTrees.OOBTree import OOBTree

LOG_KEY = 'src.plone.webauthn.connector.keydata'

class IKeyData(zope.interface.Interface):
    """ Marker interface for User """

@zope.interface.implementer(IKeyData)
class KeyDataAdapter(object):
    """ An adapter for storing user information as an annotation
        on a persistent object.
    """

    def __init__(self, context):
        self.context = context

    @property
    def annotations(self):
        all_annotations = IAnnotations(self.context)
        if LOG_KEY not in all_annotations:
            all_annotations[LOG_KEY] = OOBTree()
        return all_annotations[LOG_KEY]

    @property
    def keys(self):
        return self.annotations.values()
    
    def get_key_by_user_id(self, user_id):
        """ Find a user by uuid """
        for key in self.keys:
            if user_id == key.get('user_id'):
                return key
        raise ValueError(
            f'No key Found user_id {user_id} found')
    
    def add_key(self, user_id, data):
        if not data:
            raise ValueError("data cannot be None")
        
        self.annotations[user_id] = self.annotations.get(data, []).append(data)

        
    
    def clear(self):
        """ Delete all keys data"""
        annotations = IAnnotations(self.context)
        annotations[LOG_KEY] = OOBTree()