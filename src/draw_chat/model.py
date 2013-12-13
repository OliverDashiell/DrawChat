'''
Created on 1 Dec 2013

@author: dashb
'''

from sqlalchemy.types import String, Integer, DateTime, Boolean
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative.api import declared_attr, has_inherited_table, declarative_base
import re  # @UnresolvedImport
import datetime


#see: http://docs.sqlalchemy.org/en/rel_0_8/orm/extensions/declarative.html#augmenting-the-base

class _Base_(object):
    ''' provides default tablename and table_args properties'''

    __table_args__ = {'mysql_engine': 'InnoDB'}

    @declared_attr
    def __tablename__(self):
        if has_inherited_table(self):
            return None
        name = self.__name__
        return (name[0].lower() +
            re.sub(r'([A-Z])', lambda m:'_' + m.group(0).lower(), name[1:]))

Base = declarative_base(cls=_Base_)


session_users_user = Table('session_users_user', Base.metadata,
    Column('users_id', Integer, ForeignKey('session.id')),
    Column('user_id', Integer, ForeignKey('user.id')),
    mysql_engine='InnoDB')


class ChatObject(Base):
    
    id = Column(Integer, primary_key=True)
    type = Column(String(255))
    
    __mapper_args__ = {
        'polymorphic_identity':'chat_object',
        'polymorphic_on':type
    }
    
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship('User', uselist=False,
        primaryjoin='ChatObject.owner_id==User.id', remote_side='User.id')
    point_x = Column(Integer,default=0)
    point_y = Column(Integer,default=0)
    posted = Column(DateTime, default=datetime.datetime.now)
    color = Column(String(255), default="black")
    chat_session_id = Column(Integer, ForeignKey('session.id'))
    chat_session = relationship('Session', uselist=False,
        primaryjoin='ChatObject.chat_session_id==Session.id', remote_side='Session.id',
        back_populates='chat_objects')
    
    
    def attrs_to_dict(self):
        return {
                "color": self.color,
                "point_x": self.point_x,
                "point_y": self.point_y,
                }
    
    
    def attrs_from_dict(self, values):
        self.color = values.get("color", self.color)
        self.point_x = values.get("point_x", self.point_x)
        self.point_y = values.get("point_y", self.point_y)



class Text(ChatObject):
    __mapper_args__ = {
        'polymorphic_identity':'chat_text',
    }
    
    value = Column(String(255), default="")
    
    
    def attrs_to_dict(self):
        result = ChatObject.attrs_to_dict(self)
        result["value"] = self.value
        return result
    
    
    def attrs_from_dict(self, values):
        ChatObject.attrs_from_dict(self, values)
        self.value = values.get("value", self.value)
    
    
class Line(ChatObject):
    __mapper_args__ = {
        'polymorphic_identity':'chat_line',
    }
    
    polygon = Column(String(255), default="")
    
    
    def attrs_to_dict(self):
        result = ChatObject.attrs_to_dict(self)
        result["polygon"] = self.polygon
        return result
    
    
    def attrs_from_dict(self, values):
        ChatObject.attrs_from_dict(self, values)
        self.polygon = values.get("polygon", self.polygon)
        
    
class Shape(Line):
    __mapper_args__ = {
        'polymorphic_identity':'chat_shape',
    }
    
    fill_color = Column(String(255), default="white")
    
    
    def attrs_to_dict(self):
        result = Line.attrs_to_dict(self)
        result["fill_color"] = self.fill_color
        return result
    
    
    def attrs_from_dict(self, values):
        Line.attrs_from_dict(self, values)
        self.fill_color = values.get("fill_color", self.fill_color)
    
    

class Session(Base):
    
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.now)
    ended = Column(Boolean, default=False)
    users = relationship('User',
        primaryjoin='Session.id==session_users_user.c.users_id',
        secondaryjoin='User.id==session_users_user.c.user_id',
        secondary='session_users_user',
        lazy='joined', back_populates='sessions')
    chat_objects = relationship('ChatObject', uselist=True, 
        primaryjoin='ChatObject.chat_session_id==Session.id', remote_side='ChatObject.chat_session_id',
        back_populates='chat_session')


class User(Base):
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    sessions = relationship('Session',
        secondaryjoin='Session.id==session_users_user.c.users_id',
        primaryjoin='User.id==session_users_user.c.user_id',
        secondary='session_users_user',
        lazy='joined', back_populates='users')

    
    
