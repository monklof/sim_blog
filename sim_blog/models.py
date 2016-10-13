from sqlalchemy import create_engine, func, ForeignKey, Column
from sqlalchemy.types import String, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("mysql+mysqlconnector://USERNAME:PASSWORD@127.0.0.1/sim_blog")
# support emoji(utf8mb4) 
engine.execute("set names utf8mb4;")
MapBase = declarative_base(bind=engine)
DBSession = sessionmaker(bind=engine)

class USER_TYPE:
    ADMIN = "admin"
    GUEST = "guest"

class COMMENT_STATE:
    ACTIVE = "active"
    DELETED = "deleted"

class User(MapBase):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), nullable=False, unique=True)
    password = Column(String(2048), nullable=False)
    email = Column(String(64), nullable=False)
    url = Column(String(2048))
    
    role = Column(String(64), nullable=False)

    def __repr__(self):
        return "<User: {0}>".format(self.username)

class Post(MapBase):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    title = Column(String(64), nullable=False)
    pub_date = Column(DateTime, default=func.now(), nullable=False)
    is_published = Column(Boolean, default=True, nullable=False)
    html_text = Column(Text, nullable=False)
    md_text = Column(Text, nullable=False)
    summary = Column(String(1024), nullable=True)

    category_id = Column(Integer, ForeignKey("category.id"), nullable=True)
    category = relationship("Category", backref=backref('posts', uselist=True))
    tags = relationship("Tag", secondary="post_tag_link")

    def __repr__(self):
        return "<post> {0}".format(self.title)

# class Page(MapBase):
#     __tablename__ = "page"
#     id = Column(Integer, primary_key=True)
#     name = Column(String(1024), unique=True, nullable=False)
#     post_id = Column(Integer, ForeignKey("post.id"), nullable=False)
#     post = relationship("Post")

class Category(MapBase):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    text = Column(String(128), unique=True)

class Tag(MapBase):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True)
    text = Column(String(128), unique=True)
    posts = relationship("Post", secondary="post_tag_link")

class PostTagLink(MapBase):
    __tablename__ = "post_tag_link"
    post_id = Column(Integer, ForeignKey("post.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag.id"), primary_key=True)


class Comment(MapBase):
    __tablename__ = "comment"
    id = Column(Integer(), primary_key=True)
    author_name = Column(String(64), nullable=False)
    author_url = Column(String(64))
    author_email = Column(String(32), nullable=False)
    pub_date = Column(DateTime, default=func.now())
    text = Column(Text, nullable=False)
    html_text = Column(Text)
    post_id = Column(Integer, ForeignKey("post.id"))
    onpost = relationship(Post, backref=backref('comments', uselist=True))

    at_commentids = Column(String(128), nullable=True)
    
    state = Column(String(64), nullable=False, default=COMMENT_STATE.ACTIVE)
    def __repr__(self):
        return "<comment> {0}: {1}".format(self.author_name, self.text)

class Captcha(MapBase):
    __tablename__ = "__captcha__"

    id = Column(Integer, primary_key=True)
    code = Column(String(1024), nullable=False)
    saved_file = Column(String(1024), nullable=False)
    create_time = Column(DateTime, default=func.now())

    

MapBase.metadata.create_all()
