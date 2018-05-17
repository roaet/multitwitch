import configparser
import os
import time

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

import multitwitch.lib.communitylist as CL
from multitwitch.models import initialize_sql


class RegistryStub(object):
    def __init__(self, config):
        self.config = config

    @property
    def settings(self):
        return self.config

class RequestStub(object):
    def __init__(self, session, config):
        self.session = session
        self.config = config
        self._registry = RegistryStub(self.config)

    @property
    def registry(self):
        return self._registry

    @property
    def db(self):
        return self.session


def main():
    """ This function returns a Pyramid WSGI application.
    """
    config = configparser.ConfigParser()
    dev = bool(os.environ.get("DEV", False))

    conf_name = 'development' if dev else 'production'
    conf_name = '%s.ini' % conf_name
    conf_path = '../multitwitch_confs'
    conf_name = '%s/%s' % (conf_path, conf_name)
    print("Using conf %s" % conf_name)
    config.read(conf_name)
    engine = engine_from_config(config['app:main'], prefix='sqlalchemy.')
    initialize_sql(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    request = RequestStub(session, config['app:main'])

    comlist = CL.CommunityList(request)
    while 1:
        try:
            comobj = comlist.get_oldest_community(60)
            if comobj is not None:
                com = comobj.twitch_name
                print("Updating %s" % com)
                comlist.commit_community_update_time(com)
                comlist.clear_community_stream_list(com, commit=False)
                comlist.populate_community_streams(com, commit=False)
                session.commit()
            time.sleep(5)
        except Exception as e:
            print("Caught exception and waiting. %s" % e)
            time.sleep(30)


if __name__ == '__main__':
    main()
