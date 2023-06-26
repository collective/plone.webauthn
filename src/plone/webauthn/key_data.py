import zope.interface
import plone.api
from zope.annotation.interfaces import IAnnotations
from BTrees.OOBTree import OOBTree

LOG_KEY = 'plone.webauthn.connector.keydata'

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
        return self.annotations
    
    def get_key_by_user_id(self, user_id):
        """ Find a user by uuid """
        for key in list(self.keys.keys()):
            if user_id == key:
                return self.annotations[key]
            
        raise ValueError(
            f'No key Found user_id {user_id} found')
    
    def add_key(self, user_id, data):
        if not data:
            raise ValueError("data cannot be None")
        
        self.annotations[user_id] = self.annotations.get(user_id, list())
        self.annotations[user_id].append(data)
        self.annotations._p_changed = 1

    
    def update_key(self, user_id, new_data):

        for k, v in new_data.items():
            self.annotations[user_id][0][k] = v
        
    
    def clear(self):
        """ Delete all keys data"""
        annotations = IAnnotations(self.context)
        annotations[LOG_KEY] = OOBTree()
