from merryweb.webbase import BaseHandler
import models
from sqlalchemy.orm.exc import NoResultFound

class BlogBaseHandler(BaseHandler):
    def initialize(self, *args, **kwargs):
        pass
        
    def get_current_user(self):
        if not hasattr(self, "_user"):
            userid = self.get_secure_cookie("userid")
            if not userid:
                self._user = None
            else:
                try:
                    userid = userid.decode()
                    self._user = self.session.query(models.User).filter(models.User.id==userid).one()
                except NoResultFound: 
                    self.clear_cookie("userid")
                    self._user = None
        return self._user

    @property
    def session(self):
        if not hasattr(self, "_session"):
            self._session = models.DBSession()
        return self._session
    def on_finish(self):
        if hasattr(self, "_session"):
            self._session.close()

class AdminBaseHandler(BlogBaseHandler):
    def get_current_user(self):
        u = super().get_current_user()
        if not u or u.role != models.USER_TYPE.ADMIN:
            return None
        return u
    
