import operator

import multitwitch.lib.streamlister as sl


class CommunityList(object):
    def __init__(self, config):
        self.conf = config
        self.community_dict = self._parse_config_list()

    def _parse_config_list(self):
        community_conf_dict = [
            x for x in self.conf.items('community_list')
            if x[0] not in self.conf.defaults()
        ]

        streamlister = sl.StreamLister(self.conf)
        conf_dict = {}
        default_community = self.conf['DEFAULT'].get('default_community', '')
        for twitch_name, web_name in community_conf_dict:
            community_streams = streamlister.get_community_streams_by_name(
                twitch_name)
            community_streams = sorted(
                community_streams,
                key=lambda k : k['viewers'],
                reverse=True
            )
            conf_dict[twitch_name] = {
                'streams': community_streams,
                'web_name': web_name,
                'default': True if twitch_name == default_community else False
            }
        return conf_dict

    def get_communities(self):
        return self.community_dict
