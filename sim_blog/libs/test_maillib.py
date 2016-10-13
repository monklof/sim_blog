import signal
from maillib import MailBox, Email
from nose.tools import nottest
from functools import wraps


class EmailTestTimeoutError(Exception):
    pass

def raise_timeout_exception(*args, **kwargs):
    raise EmailTestTimeoutError()

config = {
    "smtp_server":"smtp.gmail.com",
    "smtp_port":587,
    "enable_tls":True,
    "enable_ssl":False,
    "username":"monklof@gmail.com",
    "password":"gmailcc0826",
    "mail": Email(**{
        "sender":"monklof.com <monklof@gmail.com>",
        "receivers": ["740241359@qq.com"],
        "subject":"么么哒",
        "content":"<h1>Miao, Miao, Miao~</h1>",
        "content_type":"html"
        }),
}

@nottest
def supports_timeouts(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        signal.signal(signal.SIGALRM, raise_timeout_exception)
        result = fn(*args, **kwargs)
        signal.alarm(0)
        signal.signal(signal.SIGALRM, lambda signalnum, handler: None)
        return result
    return wrapped

class TestMailBox(object):

    @classmethod
    @supports_timeouts
    def setup_class(cls):
        signal.alarm(10)
        cls.mailbox = MailBox(config["smtp_server"], config["smtp_port"], auth=(config["username"], config["password"]), enable_tls=config["enable_tls"], enable_ssl=config["enable_ssl"])
        cls.mailbox.start()

    @classmethod
    def teardown_class(cls):
        cls.mailbox.quit()

    def test_sendmail(self):
        ret = self.mailbox.send_mail(config["mail"])
        assert ret == True

    def test_callback_sync(self):
        ret = self.mailbox.send_mail(config["mail"], callback=self._mail_callback("test_callback_sync"))
        assert ret == True
        assert self.call_results["test_callback_sync"][0] == "success"

    @supports_timeouts
    def test_callback_async(self):
        ret = self.mailbox.send_mail(config["mail"], async=True, callback=self._mail_callback("test_callback_async"))
        assert ret == True

        signal.alarm(10)
        
        while not self.call_results["test_callback_async"]:
            continue
        assert self.call_results["test_callback_async"][0] == "success"

    def _mail_callback(self, call_name):
        if not hasattr(self, "call_results"):
            self.call_results = dict()
        self.call_results[call_name] = None

        def callback(status, mail):
            self.call_results[call_name] = (status, mail)

        return callback
        
