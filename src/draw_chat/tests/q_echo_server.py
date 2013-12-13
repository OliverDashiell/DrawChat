'''
Created on 5 Dec 2013

@author: dash
'''
import tornado.ioloop
import tornado.web
from tornado import websocket

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")
        
class EchoWebSocket(websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message("You said: " + message)

    def on_close(self):
        print("WebSocket closed")

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/ws", EchoWebSocket),
])

if __name__ == "__main__":
    application.listen(1234)
    tornado.ioloop.IOLoop.instance().start()