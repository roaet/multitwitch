import json

import multitwitch.lib.twitch as T


class StreamLister(object):
    def __init__(self, request):
        self.twitch_api = T.Twitch(request)
        self.conf = request.registry.settings
        self.request = request

    def _get_list_info_dict_for_team_users(self, json_object):
        stream_info = {}
        stream_info['name'] = json_object['name']
        stream_info['url'] = json_object['url']
        stream_info['description'] = json_object['status']
        stream_info['preview'] = json_object['logo']
        stream_info['game'] = json_object['game']
        stream_info['id'] = json_object['_id']
        return stream_info

    def _get_list_info_dict(self, json_object):
        stream_info = {}
        stream_info['name'] = json_object['channel']['name']
        stream_info['url'] = json_object['channel']['url']
        if 'description' in json_object['channel']:
            stream_info['description'] = json_object['channel']['description']
        elif 'status' in json_object['channel']:
            stream_info['description'] = json_object['channel']['status']
        else:
            stream_info['description'] = ""
        stream_info['game'] = json_object['channel']['game']
        stream_info['id'] = json_object['_id']
        if 'preview' in json_object:
            stream_info['preview'] = json_object['preview']['medium']
        elif 'logo' in json_object:
            stream_info['preview'] = json_object['logo']
        if 'stream_type' in json_object:
            stream_info['stream_type'] = json_object['stream_type']
        if 'viewers' in json_object:
            stream_info['viewers'] = json_object['viewers']
        return stream_info

    def get_team_streams_by_name(self, name):
        team_json = self.twitch_api.get_team_info_by_name(name)
        team_id = team_json.get('_id', None)
        if team_id is None:
            return []
        list_info = [] 
        for stream in team_json['users']:
            list_info.append(self._get_list_info_dict_for_team_users(stream))
        return list_info

    def get_stream_by_name(self, name):
        stream_json = self.twitch_api.get_stream_info_by_name(name)
        return stream_json

    def stream_is_online(self, name):
        stream = self.get_stream_by_name(name)
        return stream != None

    def get_community_streams_by_name(self, name):
        community_json = self.twitch_api.get_community_info_by_name(name)
        community_id = community_json.get('_id', None)
        if community_id is None:
            return []
        streams = self.twitch_api.get_streams_by_community_id(community_id)
        list_info = [] 
        for stream in streams:
            list_info.append(self._get_list_info_dict(stream))
        return list_info

    def get_staff_picks(self):
        streams = self.twitch_api.followed_channels_for_clientid()

        list_info = [] 
        for stream in streams:
            list_info.append(self._get_list_info_dict(stream))
        return list_info
