'''
Created on 1 Dec 2013

@author: dashb
'''
import unittest  # @UnresolvedImport
from draw_chat.control import Control
from draw_chat import model
import datetime


class Test(unittest.TestCase):


    def setUp(self):
        self.control = Control()
        self.control._drop_all_and_create_()


    def tearDown(self):
        self.control._dispose_()
        
        
    @property
    def session(self):
        return self.control._session_


    def testUser(self):
        with self.session as session:
            user = model.User(username="bert",password="bert")
            session.add(user)
            session.commit()
            self.assertEquals(user,session.query(model.User).get(1))


    def testSession(self):
        with self.session as session:
            user = model.User(username="bert",password="bert")
            session.add(user)
            user.sessions.append(model.Session())
            session.commit()
            
            self.assertGreater(datetime.datetime.now(), user.sessions[0].created)
            
            
    def testChatObject(self):
        with self.session as session:
            user = model.User(username="bert",password="bert")
            session.add(user)
            chat_session = model.Session()
            user.sessions.append(chat_session)
            
            text = model.Text(owner=user,value="foo",color="red",point_x=10,point_y=10);
            chat_session.chat_objects.append(text)
            session.commit()
            
            obj = session.query(model.ChatObject).get(1)
            self.assertEquals(obj.value,text.value)
            self.assertEquals(obj.color,text.color)
            self.assertEquals(obj.point_x,text.point_x)
            self.assertEquals(obj.point_y,text.point_y)
            self.assertEquals(obj.owner,text.owner)
            self.assertEquals(obj.type,"chat_text")
            

    def testRegister(self):
        user = self.control.register(username="bert",password="bert")
        with self.session as session:
            self.assertEquals(user['username'],session.query(model.User).get(1).username)
            self.assertEquals(user['type_'],"User")
        
        try:
            self.control.register(username="bert",password="bert")
        except Exception as ex:
            self.assertEquals(str(ex),"username already exists")


    def testLogin(self):
        self.control.register(username="bert",password="bert")
        user = self.control.login(username="bert",password="bert")
        with self.session as session:
            self.assertEquals(user['username'],session.query(model.User).get(1).username)
            self.assertEquals(user['type_'],"User")
            
        try:
            self.control.login("bert","berty")
            self.assertFalse(True, "should not reach here")
        except Exception as ex:
            self.assertEquals(str(ex),"No such user or password!")


    def testChatSession(self):
        user = self.control.register(username="bert",password="bert")
        chat_session = self.control.session_start(user["id"])
        self.assertEquals(chat_session['users'],[1])
        self.assertEquals(chat_session['ended'],False)
        
        ended_session = self.control.session_end(user["id"], chat_session["id"])
        self.assertEquals(ended_session['ended'],True)
        

    def testFriends(self):
        bert = self.control.register(username="bert",password="bert")
        ernie = self.control.register(username="ernie",password="ernie")
        bertf = self.control.add_friend(bert["id"], ernie["username"])
        
        self.assertEquals(bertf["my_friends"],[2])
        
        ernief = self.control.login(username="ernie",password="ernie")
        self.assertEquals(ernief["my_invites"],[1])
        

    def testAddFriendToSession(self):
        bert = self.control.register(username="bert",password="bert")
        ernie = self.control.register(username="ernie",password="ernie")
        chat_session = self.control.session_start(bert["id"])
        
        chat_sessionf = self.control.add_friend_to_session(bert["id"], chat_session["id"], ernie["id"])
        self.assertEquals(chat_sessionf["users"],[1,2])
        
        
    def test_chat_objects(self):
        bert = self.control.register(username="bert",password="bert")
        chat_session = self.control.session_start(bert["id"])
        text_obj = self.control.draw_chat_object(bert["id"],chat_session["id"],"chat_text",
                                                 **{"color": "red",
                                                    "point_x": 10,
                                                    "point_y": 10,
                                                    "value": "foo",
                                                    })
        chat_object_id = text_obj.get("chat_objects")[0].get("id")
        self.assertEquals("red",text_obj.get("chat_objects")[0].get("attrs").get("color"))
        
        updated_obj = self.control.update_chat_object(bert["id"], chat_object_id,color="orange")
        self.assertEquals("orange",updated_obj.get("chat_objects")[0].get("attrs").get("color"))
        chat_object_id = updated_obj.get("chat_objects")[0].get("id")
        
        self.assertTrue(self.control.delete_chat_object(bert["id"], chat_object_id))
        


            

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()