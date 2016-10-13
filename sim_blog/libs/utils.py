import subprocess, io,os
from settings import MARKDOWN_GFMRENDER_CMD

from settings import CAPTCHA_PATH, CAPTCHA_EXPIRE_TIME
from models import Captcha, DBSession
from .captcha.caplib import CaptchaGenerator
from sqlalchemy.orm.exc import NoResultFound

import datetime
import tempfile

class Logger:
    @classmethod
    def warn(cls, tip, detail):
        print("[warn] ", tip, detail)

class CaptchaHelper:
    """Util to create/check/expire an captcha"""

    g = CaptchaGenerator(CAPTCHA_PATH)
    @classmethod
    def create_captcha(cls):
        code, filename,absname = cls.g.create_one()
        c = Captcha(code=code, saved_file=absname)
        s = DBSession()
        s.add(c)
        s.commit()
        id = c.id
        s.close()
        return id, filename

    @classmethod
    def check_captcha(cls, id, code):
        s = DBSession()
        try:
            cap = s.query(Captcha).filter_by(id=id).one()
        except NoResultFound:
            s.close()
            return False
        if (datetime.datetime.now() - cap.create_time).total_seconds() > CAPTCHA_EXPIRE_TIME:
            s.delete(cap);s.commit();s.close()
            return False
        if cap.code != code:
            s.delete(cap);s.commit();s.close()
            return False
        s.delete(cap);s.commit();s.close()
        return True
    
def render_gfm(text):
    stderr_file = tempfile.TemporaryFile()
    cmd = os.path.join(os.path.dirname(__file__), MARKDOWN_GFMRENDER_CMD)
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr_file, shell=True)
    p.stdin.write(text.encode("utf-8"))
    p.stdin.close()
    p.wait()
    if p.returncode != 0:
        stderr_file.seek(0)
        error_msg = stderr_file.read()
        Logger.warn("Render GFM Failed", "ERROR MSG: %s" % error_msg)
        raise Exception("Render GFM Failed", error_msg)

    return p.stdout.read().decode("utf-8")


