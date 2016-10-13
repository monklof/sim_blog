MARKDOWN_GFMRENDER_CMD = "/usr/bin/env marked --gfm --breaks --tables --lang-prefix"

CAPTCHA_PATH = "/var/www/monklof.com/captcha/"
CAPTCHA_EXPIRE_TIME = 5*60

HOST_MAILBOX_CONF = {
    "smtp_server":"smtp.gmail.com",
    "smtp_port":587,
    "enable_tls":True,
    "enable_ssl":False,
    "username":"YOURNAMEN@gmail.com",
    "password":"YOURPASSWORD",
}

HOST_NOTIFY_MAIL = HOST_MAILBOX_CONF["username"]

