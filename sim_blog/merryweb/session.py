import random
import time
import pymongo

class SessionNotExits(Exception):
    pass

class TimeOutError(Exception):
    pass

class MongoSession:
    """
    存储会话数据，目前回话容器集合是：sessions.sessions
    {
       "sessionId":str,
       "lastAccessTime":time.time()
       "value":..，存储具体的数据
    }
    """

    create_lock = False
    def __init__(self, *, session_collection_name = "sessions", session_id=None, 
                 create = False, init_data = {}):

        self.session_bucket = pymongo.Connection()["sessions"][session_collection_name]
        
        if create:
            self.__lock()
            try:
                self.__create_new_session(init_data)
            except TimeOutError as e:
                # 解锁
                self.__unlock()
                raise e
            except Exception as e:
                self.__unlock()
                raise e
            else:
                self.__unlock()
        else:
            self.session_rc = self.session_bucket.find_one({"sessionId":session_id}, {"_id":0})
            if not self.session_rc:
                raise SessionNotExits("Session Not Exits With Id: {0}".format(session_id))

    def get_session_id(self):
        return self.session_rc["sessionId"]
    def set_session_value(self, value_data):
        self.session_rc["value"] = value_data
        self.session_bucket.update({"sessionId":self.session_rc["sessionId"]}, self.session_rc)
    def get_session_value(self):
        return self.session_rc["value"]
    def clear(self):
        self.session_bucket.remove({"sessionId":self.session_rc["sessionId"]})
        self.session_rc = None
        return True
    
    def __create_new_session(self, init_data):
        try_times = 0
        while True:
            try_times += 1
            if try_times > 10:
                raise TimeOutError("Create New Sesssion Faild!")
            session_id = self.__rand_str()
            if not self.session_bucket.find_one({"sessionId":session_id}):
                break
        session_rc = {
            "sessionId":session_id,
            "value":init_data,
            "createTime":time.time(),
            "lastAccessTime":time.time()
            }
        self.session_bucket.insert(session_rc)
        self.session_rc = session_rc

    def __rand_str(self, rand_length = 20):
        chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        length = len(chars) - 1
        rand_str = ""
        for i in range(rand_length):
            rand_str+=chars[random.randint(0, length)]
        return rand_str
    def __lock(self):
        # 等待锁
        while MongoSession.create_lock:
            # 随机等待0~100ms
            time.sleep(random.random()/10)
        # 锁住
        MongoSession.create_lock = True
    def __unlock(self):
        MongoSession.create_lock = False
