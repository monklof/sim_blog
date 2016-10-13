
import json
from collections import OrderedDict
from sqlalchemy.orm.exc import NoResultFound
import re


from settings import HOST_NOTIFY_MAIL
from handlers.base  import BlogBaseHandler
import models
from libs.utils import CaptchaHelper
from libs.maillib import Email


class About(BlogBaseHandler):
    def get(self):
        return self.render("about.html")
    def title(self):
        return "关于我 | Monklof思考和写字的地方"

class Geeks(BlogBaseHandler):
    def get(self):
        return self.render("geeks.html")
    def title(self):
        return "极客们 | Monklof思考和写字的地方"

class Home(BlogBaseHandler):
    @BlogBaseHandler.check_arguments("page?:int")
    def get(self):
        page = self.args.get("page", 1)
        posts = self.session.query(models.Post).\
                filter(models.Post.is_published==True).\
                order_by(models.Post.pub_date.desc()).offset((page-1)*10).limit(11).all()
        if len(posts) > 0 and page > 1:
            pre=page-1
        else:
            pre=None
        if len(posts) > 10:
            next = page + 1;
        else:
            next = None
        return self.render("home.html", posts=posts, page=page, pre=pre, next=next)

    def title(self):
        return "博客 | Monklof思考和写字的地方"

class Post(BlogBaseHandler):
    
    def get(self, post_spec):
        """post_spec可能是文章代号，也可能是post id"""
        
        post_spec = str(post_spec)
        if post_spec.isdigit():
            post_id = int(post_spec)
            try:
                self.p = self.session.query(models.Post).\
                  filter(models.Post.id == post_id, 
                         models.Post.is_published==True).one()

            except NoResultFound:
                return self.send_error(404)
        else:
            post_code = post_spec
            try:
                self.p = self.session.query(models.Post).\
                  filter(models.Post.code == post_code, 
                         models.Post.is_published==True).one()

            except NoResultFound:
                return self.send_error(404)
            
        author = json.loads(self.get_secure_cookie("author").decode()) if self.get_secure_cookie("author") else dict(author_name="",author_url="",author_email="")

        return self.render('post.html', 
                           context=dict(post = self.p, author=author))
    def title(self):
        return "{0} | Monklof思考和写字的地方".format(self.p.title)

class Comment(BlogBaseHandler):
    _MENTION_REG = re.compile("@\[([\w|\s|\d|\-|_]+)]\s+")
    
    @BlogBaseHandler.check_arguments("author_name", 
                                     "author_email",
                                     "author_url?",
                                     "text",
                                     "cap_id:int",
                                     "cap_code")
    def post(self, post_id):
        if not CaptchaHelper.check_captcha(self.args['cap_id'], self.args['cap_code']):
            return self.send_fail(error_text = "Captcha code error or timeout.")
        
        try:
            p = self.session.query(models.Post).\
                filter(models.Post.id == post_id,
                       models.Post.is_published==True).one()
        except NoResultFound:
            return self.send_error(404)
        author_name = self.args["author_name"].strip()
        author_url = self.args.get("author_url", "").strip()
        author_email = self.args["author_email"].strip()
        text = self.args["text"].strip()
        html_text = self.format_text(text)
        
        if not author_name or not author_email or not text:
            return self.send_fail(error_text="Please fill the columns necessary")
        self.set_secure_cookie("author", json.dumps(dict(author_name=author_name,
                                                         author_url=author_url,
                                                         author_email=author_email)))
        
        comment = models.Comment(author_name=author_name,
                                 author_url=author_url,
                                 author_email=author_email,
                                 text=text,
                                 html_text=html_text)
        p.comments.append(comment)
        self.session.commit()

        # send email notify 
        receivers = self._get_mentioned_email(comment)
        if receivers:
            self._send_comment_notify(receivers, comment)
        self._send_master_notify(comment)
        
        self.send_success()

    def _get_mentioned_email(self, comment):
        """get mentioned user in the comment in the same post"""
        names = set(self._MENTION_REG.findall(comment.text))
        emails = set()

        for name in names:
            cmts = self.session.query(models.Comment).filter_by(post_id=comment.post_id, author_name=name).all()
            for cmt in cmts:
                if cmt.author_email:
                    emails.add(cmt.author_email)
        return emails

    def _send_comment_notify(self, toaddrs, comment):
        """Send mail mention to the "@" user """
        from_addr = HOST_NOTIFY_MAIL
        mail_content = self.render_string("reply-mail-tmpl.html", comment = comment, post=comment.onpost).decode()
        subject = "Re: Comment on %s" % comment.onpost.title

        for addr in toaddrs:
            self.application.mailbox.send_mail(
                Email(
                from_addr, [addr], subject=subject,
                content=mail_content, content_type = "html"), async=True)
        
    def _send_master_notify(self, comment):
        """send mail mention to the master"""
        from_addr = HOST_NOTIFY_MAIL
        addrs = [HOST_NOTIFY_MAIL]
        mail_content = self.render_string("reply-notify-master-tmpl.html", comment = comment, post=comment.onpost).decode()
        subject = "Have comment on post %s" % comment.onpost.title

        self.application.mailbox.send_mail(Email(
            from_addr, addrs, subject=subject,
            content=mail_content, content_type = "html"), async=True)
        
        

class CaptchaHandler(BlogBaseHandler):

    def post(self):
        id, filename = CaptchaHelper.create_captcha()
        self.send_success(capid=id, capsrc = self.reverse_url("capStatic", filename))
    
class ArchiveHandler(BlogBaseHandler):
    def get(self):
        posts = self.session.query(models.Post).filter_by(is_published=True).order_by(models.Post.pub_date.desc()).all()

        archive = OrderedDict()
        for p in posts:
            year = p.pub_date.year
            if year not in archive:
                archive[year] = []
            archive[year].append(p)

        return self.render("archive.html", archive = archive)

    def title(self):
        return "博客归档 | Monklof思考和写字的地方"

class TagHandler(BlogBaseHandler):
    def get(self):
        tags = self.session.query(models.Tag).order_by(models.Tag.id.desc()).all()
        total_posts = self.session.query(models.Post).filter_by(is_published=True).count()
        avg = int(total_posts/len(tags))

        pub_tag_posts = {}
        
        for t in tags:
            pub_tag_posts[t.text] = []
            for p in t.posts:
                if p.is_published: pub_tag_posts[t.text].append(p)
        
        return self.render("tag.html", tags=pub_tag_posts, avg=avg)
    def title(self):
        return "博客分类标签 | Monklof思考和写字的地方"
            









