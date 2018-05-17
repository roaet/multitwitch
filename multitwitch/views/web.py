import configparser
import requests
import json

from multitwitch.lib.session import web, ajax
from pyramid.response import FileResponse

import multitwitch.lib.communitylist as CL
import multitwitch.lib.twitch as T
import multitwitch.lib.streamlister as sl

class WebView:

    @web(template="web/home.tmpl")
    def home(request):
        config = request.registry.settings
        author_name = config.get('site.author_name')
        title = config.get('site.title', 'X3LGaming Multitwitch')
        base_url = config.get('site.base_url', 'http://x3l.tv')
        comlist = CL.CommunityList(request)
        community_dict = comlist.get_communities()

        streamlister = sl.StreamLister(request)
        author_status = streamlister.stream_is_online(author_name)

        # stream_team = 'x3lelite'
        # stream_team_streams = streamlister.get_team_streams_by_name(
        #     stream_team)
        # staff_picks = streamlister.get_staff_picks()
        stream_team_streams = []
        staff_picks = []
        return {'project' : title,
                'streams' : [],
                'communities': community_dict,
                'stream_team_streams': stream_team_streams,
                'staff_picks': staff_picks,
                'base_url' : base_url,
                'unique_streams' : [],
                'nstreams' : len([]),
                'author_status': author_status}

    @web(template="web/home.tmpl")
    def edit(request):
        config = request.registry.settings
        author_name = config.get('site.author_name')
        title = config.get('site.title', 'X3LGaming Multitwitch')
        base_url = config.get('site.base_url', 'http://x3l.tv')
        comlist = CL.CommunityList(request)
        community_dict = comlist.get_communities()

        streamlister = sl.StreamLister(request)
        author_status = streamlister.stream_is_online(author_name)

        # stream_team = 'x3lelite'
        # stream_team_streams = streamlister.get_team_streams_by_name(
        #     stream_team)
        # staff_picks = streamlister.get_staff_picks()
        path = request.path
        if path.startswith('/'): # removes front slash /edit/ -> edit/
            path = path[1:]
        if path.endswith('/'): # removes back flash
            path = path[:-1]
        path_parts = path.split("/")
        if len(path_parts) <= 1: # if only edit
            return "REDIRECT:root:"
        stream_list = path_parts
        stream_list.pop(0) # removes 'edit'
        edit_string = '/'.join(stream_list)

        return {'project' : title,
                'streams' : stream_list,
                'communities': community_dict,
                'stream_team_streams': stream_team_streams,
                'staff_picks': staff_picks,
                'base_url' : base_url,
                'unique_streams' : [],
                'edit_string': edit_string,
                'nstreams' : len(stream_list),
                'author_status': author_status}

    @web()
    def view(request):
        stream_list = []
        layout = 'layout0'
        if len(request.GET) == 0:
            return "REDIRECT:root:"
        for idx in xrange(7):
            key = 's%d' % idx
            if len(request.GET[key]) > 0:
                stream_list.append(request.GET[key])
        if len(request.GET['layout']) > 0:
            layout = "layout%s" % request.GET['layout']
        stream_list.append(layout)
        path = '/'.join(stream_list)
        return "REDIRECT:multitwitch:%s" % path

    @web(template="web/streams.tmpl")
    def streams(request):
        config = request.registry.settings
        author_name = config.get('site.author_name')
        title = config.get('site.title', 'X3LGaming Multitwitch')
        base_url = config.get('site.base_url', 'http://x3l.tv')
        comlist = CL.CommunityList(request)
        community_dict = comlist.get_communities()

        path = request.path
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/'):
            path = path[:-1]
        path_parts = path.split("/")
        if len(path_parts) <= 1:
            return "REDIRECT:root:"
        if 'layout' not in path_parts[-1]:
            path = '/'.join(path_parts)
            path = '%s/layout0' % path
            return "REDIRECT:multitwitch:%s" % path
        stream_list = path_parts[:-1]
        edit_string = '/'.join(stream_list)
        return {'project' : title,
                'streams' : stream_list,
                'base_url' : base_url,
                'unique_streams' : [],
                'edit_string': edit_string,
                'nstreams' : len(stream_list)}

    @staticmethod
    def favicon(request):
        return FileResponse("multitwitch/static/favicon.ico", content_type="image/x-icon")
