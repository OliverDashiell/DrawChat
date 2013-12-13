'''
Created on 2 Dec 2013

@author: dashb
'''
import tornado.ioloop
import tornado.web
from draw_chat.rpc_handler import RPCWebSocket
from tornado.options import define, options, parse_command_line
from draw_chat.control import Control
import logging  # @UnresolvedImport


define("db_url", default="sqlite:///chat_objects.db", help="Main DB")
define("port", 8080, int, help="port to listen on")
define("debug", True, bool, help="reloadable")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("This is just an rpc server for websockets")
        

def main():
    parse_command_line()
    
    control = Control(options.db_url)
    control._drop_all_and_create_()
    
    handlers = [
        (r"/websocket", RPCWebSocket),
        (r"/(.*)", MainHandler),
    ]
    settings = {
        "control": control,
        "debug": options.debug
    }
    
    application = tornado.web.Application(handlers,**settings)
    application.listen(options.port)
    logging.info("listening on port %s",options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()