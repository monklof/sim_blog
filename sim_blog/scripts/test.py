import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from models import DBSession, Post, Tag, PostTagLink
import random

def main():
    """修改博客标签"""
    session = DBSession()
    tags = session.query(Tag).all()
    
    for p in session.query(Post).all():
        for i in range(random.randint(0, len(tags)-1)):
            p.tags.append(tags[i])
    session.commit()
    session.close()

if __name__ == "__main__":
    main()
