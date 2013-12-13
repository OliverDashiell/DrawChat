'''
Created on 2 Dec 2013

@author: dashb
'''
from tornado import websocket
from tornado.escape import json_decode
import logging  # @UnresolvedImport


class RPCWebSocket(websocket.WebSocketHandler):
    
    @property
    def control(self):
        return self.application.settings["control"]
    
    def open(self):
        self.user_id = None
        self.control._add_client_(self)
        

    def on_message(self, raw_message):
        logging.debug(raw_message)
        message = json_decode(raw_message)
        request_id = message.get("request_id",None)
        result = error_ = None
        try:
            action = message["action"]
            if action[0] == "_" :
                raise Exception("you many not call private methods")
            args = message.get("args",{})
            method = getattr(self.control,action)
            self.control._current_client_ = self
            result = method(**args)
        except Exception as ex:
            error_ = str(ex)
        finally:
            self.control._current_client_ = None
        self.write_message({"error":error_, "result": result, "request_id": request_id})
            
    def broadcast(self, signal,message):
        self.write_message({"signal":signal, "message":message})

    def on_close(self):
        logging.info("closing %s", self.user_id)
        self.control._remove_client_(self)
