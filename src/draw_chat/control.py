'''
Created on 1 Dec 2013

@author: dashb
'''
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.engine import create_engine, reflection
import logging  # @UnresolvedImport
from draw_chat import model
from sqlalchemy.schema import MetaData, ForeignKeyConstraint, Table,\
    DropConstraint, DropTable
from draw_chat.protocol import Protocol
from sqlalchemy.exc import IntegrityError


class Control(object):
    
    
    def __init__(self, db_url='sqlite:///:memory:', echo=False):
        params = dict(echo=echo)
        if 'mysql' in db_url:
            params['encoding']='utf-8'
            
        logging.info("connecting to db %s",db_url)
        self._engine_ = create_engine(db_url, **params)
        self._Session_ = sessionmaker(bind=self._engine_)
        self._clients = []
        self._online = {}
        self._current_client_ = None
        
        
    def _set_user_(self, user):
        if self._current_client_:
            self._current_client_.user_id = user.id if user else None
        if user:
            self._online[user.id] = Protocol.friend_protocol(user) 
            self.broadcast("online", self._online.values())
    
    
    def register(self, username, password):
        with self._session_ as session:
            user = model.User(username=username, password=password)
            session.add(user)
            try:
                session.commit()
                self._set_user_(user)
            except IntegrityError:
                raise Exception("username already exists")
            return Protocol.user_protocol(user)
    
    
    def login(self, username, password):
        with self._session_ as session:
            user = session.query(model.User).filter_by(username=username, password=password).first()
            if user is None:
                raise Exception("No such user or password!")
            self._set_user_(user)
            return Protocol.user_protocol(user)
        
    
    def logout(self, user_id):
        self._set_user_(None)
    
    
    def session_start(self, user_id):
        with self._session_ as session:
            chat_session = model.Session()
            session.add(chat_session)
            chat_session.users.append(session.query(model.User).get(user_id))
            session.commit()
            return Protocol.chat_session_protocol(chat_session)
        
    
    def session_end(self, user_id, session_id):
        with self._session_ as session:
            chat_session = session.query(model.Session).get(session_id)
            chat_session.ended = True
            session.commit()
            return Protocol.chat_session_protocol(chat_session)
        
    
    def get_chat_session(self, user_id, session_id):
        with self._session_ as session:
            user = session.query(model.User).get(user_id)
            chat_session = session.query(model.Session).get(session_id)
            
            if user not in chat_session.users:
                raise Exception("You cannot view this session")
            
            return Protocol.chat_session_protocol(chat_session)
        
    def get_friend_by_id(self, user_id, friend_id):
        with self._session_ as session:
            friend = session.query(model.User).get(friend_id)
            
            return Protocol.friend_protocol(friend);
    
    
    def add_user_to_session(self, user_id, session_id, friend_id):
        with self._session_ as session:
            user = session.query(model.User).get(user_id)
            friend = session.query(model.User).get(friend_id)
            chat_session = session.query(model.Session).get(session_id)
            
            session_users = list(chat_session.users)
            assert user in session_users
            assert friend not in session_users
            
            chat_session.users.append(friend)
            session.commit()
            
            msg = Protocol.chat_session_protocol(chat_session)
            
            for user in chat_session.users:
                self.broadcast_user(user.id, "drawn_chat_object", msg)
            
            return True
            
    
    def draw_chat_object(self, user_id, session_id, type_, **kwargs):
        with self._session_ as session:
            user = session.query(model.User).get(user_id)
            chat_session = session.query(model.Session).get(session_id)
            
            if user not in chat_session.users:
                raise Exception("You cannot add to this session")
            
            if type_ == "Text":
                result = model.Text(**kwargs)
            elif type_ == "Line":
                result = model.Line(**kwargs)
            elif type_ == "Shape":
                result = model.Shape(**kwargs)
            else:
                raise Exception("unknown type: {}".format(type_))
            
            result.owner = user
            chat_session.chat_objects.append(result)
            session.add(result)
            session.commit()
            
            msg = Protocol.chat_session_protocol(chat_session)
            
            for user in chat_session.users:
                self.broadcast_user(user.id, "drawn_chat_object", msg)
            
            return True
        
    
    
    def update_chat_object(self, user_id, chat_object_id, **kwargs):
        with self._session_ as session:
            user = session.query(model.User).get(user_id)
            chat_object = session.query(model.ChatObject).get(chat_object_id)
            
            if user not in chat_object.chat_session.users:
                raise Exception("You cannot add to this session")
            
            chat_object.attrs_from_dict(kwargs)
            session.commit()
            
            chat_session = chat_object.chat_session
            
            msg = Protocol.chat_session_protocol(chat_session)
            
            for user in chat_session.users:
                self.broadcast_user(user.id, "updated_chat_object", msg)
                
            return True
    
    
    def delete_chat_object(self, user_id, chat_object_id):
        with self._session_ as session:
            user = session.query(model.User).get(user_id)
            chat_object = session.query(model.ChatObject).get(chat_object_id)
            
            if user not in chat_object.chat_session.users:
                raise Exception("You cannot add to this session")
            
            chat_session = chat_object.chat_session
            
            session.delete(chat_object)
            session.commit()
            
            msg = Protocol.chat_session_protocol(chat_session)
            
            for user in chat_session.users:
                self.broadcast_user(user.id, "deleted_chat_object", msg)
            
            return True


    def _dispose_(self):
        ''' 
            tidy up we've gone away
        '''
        if self._engine_:
            self._engine_.dispose()
        self._Session_ = self._engine_ = None
        logging.debug("control disposed")
        
        
    @property
    def _session_(self):
        session = self._Session_()
        class closing_session:
            def __enter__(self):
                logging.debug("db session open")
                return session
            def __exit__(self, type, value, traceback):
                logging.debug("db session closed")
                session.close()
        return closing_session()
            
            
    def _drop_all_and_create_(self):
        with self._session_ as session:
            self._drop_all_(session)
            self._create_all_()


    def _create_all_(self):
        logging.info("creating schema")
        model.Base.metadata.create_all(self._engine_)  # @UndefinedVariable
        
        
    def _drop_all_(self, session):
        logging.warn("dropping schema")
        inspector = reflection.Inspector.from_engine(session.bind)
        
        # gather all data first before dropping anything.
        # some DBs lock after things have been dropped in 
        # a transaction.
        
        metadata = MetaData()
        
        tbs = []
        all_fks = []
        
        for table_name in inspector.get_table_names():
            fks = []
            for fk in inspector.get_foreign_keys(table_name):
                if not fk['name']:
                    continue
                fks.append(
                    ForeignKeyConstraint((),(),name=fk['name'])
                    )
            t = Table(table_name,metadata,*fks)
            tbs.append(t)
            all_fks.extend(fks)
        
        for fkc in all_fks:
            session.execute(DropConstraint(fkc))
        
        for table in tbs:
            session.execute(DropTable(table))
        
        session.commit()
        
        
    def _add_client_(self, client):
        self._clients.append(client)
        
        
    def _remove_client_(self, client):
        self._clients.remove(client)
        if client.user_id:
            del self._online[client.user_id]
            self.broadcast("online", self._online.values())
        
        
    def broadcast(self, signal, message):
        for client in self._clients:
            client.broadcast(signal, message)
            
    def broadcast_user(self, user_id, signal, message):
        for client in self._clients:
            if client.user_id == user_id:
                client.broadcast(signal, message)
            
            
        
