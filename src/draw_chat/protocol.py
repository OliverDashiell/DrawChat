'''
Created on 1 Dec 2013

@author: dashb
'''


class Protocol(object):
    
    
    @classmethod
    def user_protocol(cls, user):
        return {
                "username": user.username,
                "type_": user.__class__.__name__,
                "my_sessions": [{"id":s.id, "created":str(s.created)} for s in user.sessions],
                "id": user.id
                }

    
    @classmethod
    def chat_session_protocol(cls, chat_session):
        return {
                "users": [{"id": u.id, "username": u.username} for u in chat_session.users],
                "chat_objects": [cls.chat_object_protocol(o) for o in chat_session.chat_objects],
                "created": str(chat_session.created),
                "ended": str(chat_session.ended) if chat_session.ended else None,
                "type_": chat_session.__class__.__name__,
                "id": chat_session.id
            }

    
    @classmethod
    def chat_object_protocol(cls, obj):
        return {
                "attrs": obj.attrs_to_dict(),
                "posted": str(obj.posted),
                "owner_id": obj.owner_id,
                "chat_session_id": obj.chat_session_id,
                "type_": obj.__class__.__name__,
                "id": obj.id
                }
        
    @classmethod
    def friend_protocol(cls, friend):
        return {
                "type_": friend.__class__.__name__,
                "id": friend.id,
                "username": friend.username
                }
    