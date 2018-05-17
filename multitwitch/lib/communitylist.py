from datetime import datetime
from datetime import timedelta
import operator

from sqlalchemy import and_
from sqlalchemy import or_

import multitwitch.lib.streamlister as sl
from multitwitch.models.twitch_db import Community
from multitwitch.models.twitch_db import Stream


class CommunityList(object):
    def __init__(self, request, community=False, session=None):
        self.request = request
        self.conf = request.registry.settings
        self.session = request.db

        self.default_community = self.conf.get('site.default_community', '')
        self._configure_from_db()

    def _configure_from_db(self):
        if self.session is None:
            return
        conf_dict = {}
        for com in self.session.query(Community).filter(
                Community.active == 1).all():
            conf_dict[com.twitch_name] = com.display_name
        self.community_dict = conf_dict

    def _parse_config_list(self):
        conf_dict = {}
        community_conf_dict = [
            x for x in self.conf.items('community_list')
            if x[0] not in self.conf.defaults()
        ]
        for twitch_name, web_name in community_conf_dict:
            conf_dict[twitch_name] = web_name

        self.community_dict = conf_dict

    def get_community_streams_db(self, twitch_name):
        if self.session is None:
            return {}
        com = self.session.query(Community).filter(and_(
            Community.twitch_name == twitch_name,
            Community.active == 1)).one()
        streams = com.streams
        community_streams = []
        for stream in streams:
            community_streams.append(stream.to_stream_info_dict())
        return {
            'streams': community_streams,
            'web_name': com.display_name,
            'default': True if twitch_name == self.default_community else False
        }

    def get_community(self, twitch_name, web_name=None, db=True):
        if self.session is not None and db:
            return self.get_community_streams_db(twitch_name)
        if self.session is not None:
            self._configure_from_db()
        if web_name is None:
            web_name = self.community_dict[twitch_name]
        streamlister = sl.StreamLister(self.request)
        community_streams = streamlister.get_community_streams_by_name(
            twitch_name)
        community_streams = sorted(
            community_streams,
            key=lambda k : k['viewers'],
            reverse=True
        )
        return {
            'streams': community_streams,
            'web_name': web_name,
            'default': True if twitch_name == self.default_community else False
        }

    def get_oldest_community(self, min_age_sec=0):
        if self.session is None:
            return None
        current_time = datetime.utcnow()
        min_sec_ago = current_time - timedelta(seconds=min_age_sec)
        community = self.session.query(Community).filter(and_(
            Community.active == 1, or_(
            Community.last_update < min_sec_ago,
            Community.last_update == None
            ))).order_by(
            Community.last_update.asc()).first()
        return community

    def clear_community_stream_list(self, community, commit=False):
        if self.session is None:
            return None
        com = self.session.query(Community).filter(
            Community.twitch_name == community).one()
        self.session.query(Stream).filter(
            Stream.community_id == com.id).delete()
        if commit:
            self.session.commit()

    def _create_stream_object_from_dict(self, d, community=None):
        if self.session is None:
            return None
        return Stream(
            d['name'], d['url'], int(d['id']), d['description'], d['game'],
            community, d['preview'], d['stream_type'], d['viewers'])

    def populate_community_streams(self, community, commit=False):
        if self.session is None:
            return None
        com = self.session.query(Community).filter(and_(
            Community.twitch_name == community,
            Community.active == 1)).one()
        community_dict = self.get_community(com.twitch_name, db=False)
        streams = community_dict['streams']
        name_check = {}
        for stream in streams:
            if stream['name'] in name_check:
                continue
            name_check[stream['name']] = 0
            stream_object = self._create_stream_object_from_dict(
                stream, com)
            self.session.add(stream_object)
        if commit:
            self.session.commit()
        print("%s community updated %d streams" % (
            com.twitch_name, len(streams)))

    def commit_community_update_time(self, community):
        self.set_community_update_time(community, commit=True)

    def set_community_update_time(self, community, commit=False):
        if self.session is None:
            return None
        com = self.session.query(Community).filter(
            Community.twitch_name == community).one()
        com.last_update = datetime.utcnow()
        if commit:
            self.session.commit()

    def get_community_list(self):
        conf_dict = {}
        print(self.community_dict)
        for twitch_name, web_name in self.community_dict.items():
            conf_dict[twitch_name] = self.get_community(twitch_name, web_name)
        return conf_dict

    def get_communities(self):
        return self.get_community_list()
