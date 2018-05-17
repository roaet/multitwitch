import json
import requests
import time


class Twitch(object):
    def __init__(self, request):
        self.config = request.registry.settings

        self.endpoint = 'https://api.twitch.tv/kraken'
        self.clientid = self.config.get('twitch.unauthclient_id')
        self.endpoint = self.config.get('twitch.apiurl', self.endpoint)

    def _build_endpoint(self, target):
        return '/'.join([self.endpoint, target])

    def _basic_headers(self):
        headers = {
            'Client-ID': self.clientid,
            'Accept': 'application/vnd.twitchtv.v5+json'
        }
        return headers

    def _make_request(self, endpoint, payload=None, limit=25, offset=0):
        if payload and limit:
            payload['limit'] = limit
            payload['offset'] = offset
        try:
            r = requests.get(
                self._build_endpoint(endpoint),
                params=payload, headers=self._basic_headers()
            )
        except requests.exceptions.ChunkedEncodingError as e:
            print("Caught error %s" % e)
            return None
        return r

    def _make_json_request(self, endpoint, payload=None, limit=25, offset=0):
        r = self._make_request(endpoint, payload, limit, offset)
        if r is None:
            return None
        return r.json()

    def get_community_info_by_name(self, name):
        payload = {'name': name}
        community_json = self._make_json_request('communities', payload)
        return community_json

    def get_stream_info_by_name(self, name):
        payload = {'login': name}
        user_json = self._make_json_request('users', payload)
        final_user_json = None
        if len(user_json['users']) == 0:
            return None
        if len(user_json['users']) > 1:
            for users in user_json['users']:
                if user['display_name'] == name:
                    final_user_json = user
        else:
            final_user_json = user_json['users'][0]

        target = 'streams/%s' % final_user_json['_id']
        stream_json = self._make_json_request(target)
        stream_info = stream_json['stream']
        return stream_info

    def get_team_info_by_name(self, name):
        target = 'teams/%s' % name
        team_json = self._make_json_request(target)
        return team_json

    def get_streams_by_community_id(self, id):
        payload = {'community_id': id}
        limit = 100
        offset = 0
        streams = []

        streams_json = self._make_json_request(
            'streams', payload, limit=limit)
        streams.extend(streams_json['streams'])
        if streams_json and streams_json['_total'] > limit:
            while(
                streams_json and
                streams_json['_total'] > 0 and
                len(streams_json['streams']) > 0
            ):
                offset += limit
                streams_json = self._make_json_request(
                    'streams', payload, limit=limit, offset=offset)
                if streams_json is None:
                    return []
                streams.extend(streams_json['streams'])
                time.sleep(2)
        return streams

    def followed_channels_for_clientid(self, clientid=None, oauth=None):
        if (clientid is None or oauth is None) and 'twitch' in self.config:
            clientid = self.config.get('twitch.authclient_id')
            oauth = self.config.get('twitch.authclient_oath')

        path = 'https://api.twitch.tv/kraken/streams/followed'
        if 'twitch' in self.config:
            path = self.config.get('twitch.follow_apiurl', path)
        headers = {
            'Client-ID': clientid,
            'Authorization': 'OAuth %s' % oauth
        }
        r = requests.get(
            path,
            headers=headers
        )
        return r.json()['streams']
