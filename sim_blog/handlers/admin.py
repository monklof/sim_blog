import tornado.web

from handlers.base import AdminBaseHandler
import models
from sqlalchemy.orm.exc import NoResultFound
from libs.utils import render_gfm

class Login(AdminBaseHandler):
    def get(self):
        return self.render('admin/login.html')
    @AdminBaseHandler.check_arguments("username", "password")
    def post(self):
        try:
            user = self.session.query(models.User).filter(
                models.User.username==self.args["username"],
                models.User.password==self.args["password"],
                models.User.role == models.USER_TYPE.ADMIN).one()
        except NoResultFound:
            user = None
        if not user:
            return self.send_fail(error_text="username and password not match!")
        self.set_secure_cookie("userid", str(user.id).encode())
        return self.send_success(next=self.get_argument("next", 
                             self.reverse_url("adminHome")))
    def title(self):
        return "Monklof Admin"

class Logout(AdminBaseHandler):
    def get(self):
        self.clear_cookie("userid")
        return self.redirect(self.reverse_url("adminHome"))

class Home(AdminBaseHandler):
    @tornado.web.authenticated
    def get(self):
        print(self.current_user)
        posts = self.session.query(models.Post).order_by(models.Post.pub_date.desc()).all()
        return self.render("admin/home.html", posts=posts)
    def title(self):
        return "Monklof Admin"

class Post(AdminBaseHandler):
    def initialize(self, action):
        super().initialize()
        self._action = action

    @tornado.web.authenticated
    def get(self, post_id=None):
        if self._action == "addPost":
            tags = self.session.query(models.Tag).order_by(models.Tag.id.desc()).all()
            return self.render("admin/post-edit.html", post=None, error_msg_text=None, tags=tags)
        elif self._action == "editPost":
            if not post_id: return self.send_error(404)
            try:
                post = self.session.query(models.Post).filter_by(
                    id=post_id).one()
            except NoResultFound:
                post = None
            if not post: return self.send_error(404)
            tags = self.session.query(models.Tag).order_by(models.Tag.id.desc()).all()
            return self.render("admin/post-edit.html", post=post, error_msg_text=None, tags=tags)
        elif self._action == "viewPost":
            if not post_id: return self.send_error(404)
            try:
                post = self.session.query(models.Post).filter_by(
                    id=post_id).one()
            except NoResultFound:
                post = None
            if not post: return self.send_error(404)
            
            return self.render("post.html", 
                               context=dict(post=post, error_msg_text=None, 
                                            page = "adminViewPost"))
        else:
            return self.send_error(403)
    
    @tornado.web.authenticated
    def post(self, post_id=None):
        if self._action == "addPost":
            title = self.get_argument("title", "")            
            md_text = self.get_argument("md_text", "")
            is_published = bool(self.get_argument("is_published", False))
            tags = self.get_argument("tags", "")
            summary = self.get_argument("summary", "")
            
            post = self.add_post(title, md_text, is_published, tags, summary)

            return self.redirect(self.reverse_url("adminViewPost", post.id))
        elif self._action == "editPost":
            if not post_id: return self.send_error(404)
            title = self.get_argument("title", "")            
            md_text = self.get_argument("md_text", "")
            is_published = bool(self.get_argument("is_published", False))
            tags = self.get_argument("tags", "")
            summary = self.get_argument("summary", "")
            post = self.edit_post(post_id, title, md_text, is_published, tags, summary)
            if not post: return self.send_error(404)
            return self.redirect(self.reverse_url("adminViewPost", post.id))
        elif self._action == "deletePost":
            if not post_id: return self.send_error(403)
            try:
                post = self.session.query(models.Post).filter_by(id=post_id).one()
            except NoResultFound:
                post = None
            else:
                self.session.delete(post)
                self.session.commit()
            return self.redirect(self.reverse_url("adminHome"))
        else:
            return self.send_error(403)

    def get_tags(self, tag_str):
        s = self.session
        tags = []
        for t in tag_str.split(" "):
            t = t.strip()
            if not t: continue
            try:
                tag = s.query(models.Tag).filter_by(text=t).one()
            except NoResultFound:
                tag = models.Tag(text=t)
            tags.append(tag)
        return tags

    def add_post(self, title, md_text, is_published, tags, summary):
        post = models.Post(title=title, 
                           is_published=is_published,
                           md_text=md_text,
                           html_text=render_gfm(md_text),
                           summary=summary)
        self.session.add(post)
        tags = self.get_tags(tags)
        for t in tags:
            post.tags.append(t)
        self.session.commit()
        return post
    
    def edit_post(self,post_id, title, md_text, is_published, tags, summary):
        try:
            post = self.session.query(models.Post).filter_by(id=post_id).one()
        except NoResultFound:
            post = None
        else:
            post.title = title
            post.is_published = is_published
            if md_text != post.md_text:
                post.html_text = render_gfm(md_text)
            post.md_text = md_text
            post.summary = summary
            post.tags = self.get_tags(tags)
            self.session.commit()            
        return post

    def title(self):
        return "Edit/Add Post | Monklof Admin"

class Comment(AdminBaseHandler):
    def initialize(self, action):
        super().initialize()
        self._action = action

    @tornado.web.authenticated
    @AdminBaseHandler.check_arguments("comment_id:int")
    def post(self):
        if self._action == "deleteComment":
            comment_id = self.args["comment_id"]
            try:
                comment = self.session.query(models.Comment).filter_by(id = comment_id).one()
                
            except NoResultFound:
                comment = None
            if not comment: return self.send_error(404)
            comment.state = models.COMMENT_STATE.DELETED
            self.session.commit()
            return self.send_success(comment_id=comment_id)
        else:
            return self.send_error(404)

class Image(AdminBaseHandler):
    pass
