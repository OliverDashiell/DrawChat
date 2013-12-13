'''
Created on 2 Dec 2013

@author: dashb
'''
from tornado.websocket import websocket_connect
from tornado.testing import AsyncTestCase
from tornado.testing import gen_test
from tornado.escape import json_encode, json_decode
from tornado import gen

class Test(AsyncTestCase):

    @gen.coroutine
    def read_until_request_id(self, client, request_id):
        while True:
            response = yield client.read_message()
            json_response = json_decode(response)
            
            if json_response.get("error"):
                raise Exception(json_response.get("error"))
            
            if json_response.get("request_id") == request_id:
                raise gen.Return(response)
            
            print('broadcast: {}'.format(json_response))
    
    @gen_test
    def test_1_register(self):
        """first test function"""
        client = yield websocket_connect("ws://localhost:8080/websocket", self.io_loop)
        
        request_id = 0
        client.write_message(json_encode({
                                          "action":"register",
                                          "request_id": request_id,
                                          "args":{
                                                  "username":"bert", 
                                                  "password":"bert" }}))
        response = yield self.read_until_request_id(client, request_id)
        print('got: {}'.format(response))
        response = json_decode(response)
        user = response["result"]
        
        
        request_id += 1
        client.write_message(json_encode({
                                          "action":"session_start",
                                          "request_id": request_id,
                                          "args":{
                                                  "user_id":user["id"]}}))
        response = yield self.read_until_request_id(client, request_id)
        print('got: {}'.format(response))
        response = json_decode(response)
        session = response["result"]
        
        
        request_id += 1
        client.write_message(json_encode({
                                          "action":"draw_chat_object",
                                          "request_id": request_id,
                                          "args":{
                                                  "user_id":user["id"],
                                                  "session_id": session["id"],
                                                  "type_": "Text",
                                                  "color": "255:0:0:255",
                                                  "point_x": 100,
                                                  "point_y": 60,
                                                  "value": "foo2"}}))
        response = yield self.read_until_request_id(client, request_id)
        print('got: {}'.format(response))
        
        
        request_id += 1
        client.write_message(json_encode({
                                          "action":"draw_chat_object",
                                          "request_id": request_id,
                                          "args":{
                                                  "user_id":user["id"],
                                                  "session_id": session["id"],
                                                  "type_": "Text",
                                                  "color": "0:0:255:255",
                                                  "point_x": 100,
                                                  "point_y": 110,
                                                  "value": "bar2"}}))
        response = yield self.read_until_request_id(client, request_id)
        print('got: {}'.format(response))
        
        

