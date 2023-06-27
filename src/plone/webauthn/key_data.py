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
    
    def get_user_device_key(self, user_id, cname):
        return self.annotations[user_id][cname]
    
    def add_key(self, user_id, cname, data):
        if not data:
            raise ValueError("data cannot be None")
        
        if user_id not in self.annotations.keys():
            self.annotations[user_id] = {}
        
        self.annotations[user_id][cname] = data
        self.annotations._p_changed = 1

    
    def update_key(self, user_id, cname, new_data):

        for k, v in new_data.items():
            self.annotations[user_id][cname][k] = v
        
