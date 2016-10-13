#! /usr/bin/env python3

import tornado.web
import tornado.ioloop
from tornado.options import options, define

import os
import atexit
import logging
import handlers.front
import handlers.admin
from settings import CAPTCHA_PATH, HOST_MAILBOX_CONF
from libs.maillib import MailBox, MAILBOX_STATUS


class Application(tornado.web.Application):
    def __init__(self, activate_mailbox=True):
        settings = {
            "debug": bool(options.debug),
            "login_url": r"/admin/login/",

            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "static_url_prefix": "/static/",

            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "cookie_secret": "shabianishishabianishi",
            "xsrf_cookies": True
        }
        handlers_ = [
            (r"/", handlers.front.Home,{}, "home"),
            (r"/about/", handlers.front.About,{}, "about"),
            (r"/geeks/", handlers.front.Geeks,{}, "geeks"),
            (r"/archive/", handlers.front.ArchiveHandler, {}, "archive"),
            (r"/tag/",handlers.front.TagHandler, {}, "tag"),
            (r"/post/(\d+|\w)/", handlers.front.Post, {}, "post"),
            (r"/post/(\d+)/comment/", handlers.front.Comment,{}, "comment"),

            (r"/admin/login/", handlers.admin.Login, {}, "adminLogin"),
            (r"/admin/logout/", handlers.admin.Logout, {}, "adminLogout"),
            (r"/admin/", handlers.admin.Home, {}, "adminHome"),
            (r"/admin/post/add/", handlers.admin.Post, 
                                {"action":"addPost"}, "adminAddPost"),
            (r"/admin/post/(\d+)/edit/", handlers.admin.Post, 
                                {"action":"editPost"}, "adminEditPost"),
            (r"/admin/post/(\d+)/delete/", handlers.admin.Post, 
                                {"action":"deletePost"}, "adminDeletePost"),
            (r"/admin/post/(\d+)/", handlers.admin.Post, 
             {"action":"viewPost"}, "adminViewPost"),
            (r"/admin/comment/delete", handlers.admin.Comment,
             {"action":"deleteComment"}, "adminDeleteComment"),
            (r"/admin/image/upload/", handlers.admin.Image,
                                {"action":"upload"},  "adminUploadImage"),
            (r"/cap", handlers.front.CaptchaHandler),
            (r"/cap/imgs/(.*)", tornado.web.StaticFileHandler, dict(path=CAPTCHA_PATH), "capStatic"),
        ]
        
        super().__init__(handlers_, **settings)
        config = HOST_MAILBOX_CONF
        logging.info("starting mailbox server...")
        self.mailbox = MailBox(config["smtp_server"], config["smtp_port"], auth=(config["username"], config["password"]), enable_tls=config["enable_tls"], enable_ssl=config["enable_ssl"], activate=activate_mailbox)
        if self.mailbox.get_status() == MAILBOX_STATUS.CONNECTED:
            logging.info("start mailbox server success")
        else:
            logging.error("mailbox failed to connect to server!")
        self.mailbox.start()

def shutdown_app(application):
    """quit the mailbox if it's online"""
    logging.info("shutting down the mailbox server...")
    try:
        application.mailbox.quit()
    except:
        pass

def main():
    define("debug", default=0, help="debug mode: 1 to open, 0 to close")
    define("port", default=8888, help="port, defualt: 8888")
    define("enablemail", default=1, help="if need to start mail box")
    tornado.options.parse_command_line()
    app = Application(activate_mailbox=options.enablemail)
    app.listen(options.port)
    if options.debug:debug_str = "in debug mode"
    else:debug_str = "in production mode"
    logging.info("running sim_blog {0} @ {1}...".format(debug_str, 
                                                 options.port))
    atexit.register(shutdown_app,app)
    
    tornado.ioloop.IOLoop.instance().start()

    
if __name__ == "__main__":
    main()
