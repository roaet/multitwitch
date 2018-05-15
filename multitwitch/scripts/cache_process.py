import configparser
import os
import time

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

import multitwitch.lib.communitylist as CL
from multitwitch.models import initialize_sql


def main():
    """ This function returns a Pyramid WSGI application.
    """
    config = configparser.ConfigParser()
    dev = bool(os.environ.get("DEV", False))

    conf_name = 'development' if dev else 'production'
    conf_name = '%s.ini' % conf_name
    config.read(conf_name)
    engine = engine_from_config(config['app:main'], prefix='sqlalchemy.')
    initialize_sql(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    twitch_config = configparser.ConfigParser()
    twitch_config.read('config.ini')
    comlist = CL.CommunityList(twitch_config, session=session)
    while 1:
        comobj = comlist.get_oldest_community(60)
        if comobj is not None:
            com = comobj.twitch_name
            print("Updating %s" % com)
            comlist.commit_community_update_time(com)
            comlist.clear_community_stream_list(com, commit=False)
            comlist.populate_community_streams(com, commit=False)
            session.commit()
        time.sleep(5)


if __name__ == '__main__':
    main()
