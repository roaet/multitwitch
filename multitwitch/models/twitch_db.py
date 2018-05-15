import warnings

from multitwitch.models import Base
from sqlalchemy.exc import SAWarning
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Unicode
from sqlalchemy import Integer
from sqlalchemy.orm import relationship


warnings.filterwarnings(
    'ignore',
    '^Unicode type received non-unicode bind param value',
    SAWarning)


class TestModel(Base):
    __tablename__  = 'test'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value


class Stream(Base):
    __tablename__  = 'streams'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(64), unique=False)
    url = Column(Unicode(1024), unique=False)
    service_id = Column(Unicode(256), unique=False)

    description = Column(Unicode(2048))
    game = Column(Unicode(256))
    thumbnail = Column(Unicode(2048))
    stream_type = Column(Unicode(2048))
    viewers = Column(Integer)
    community_id = Column(Integer, ForeignKey('communities.id'))
    community = relationship('Community', back_populates='streams')

    def __init__(
            self, name, url, service_id, description, game, community,
            thumbnail, stream_type, viewers):
        self.name = name
        self.url = url
        self.service_id = int(service_id)
        self.description = description
        self.game = game
        self.community = community
        self.thumbnail = thumbnail
        self.stream_type = stream_type
        self.viewers = viewers

    def to_stream_info_dict(self):
        return {
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'game': self.game,
            'id': self.service_id,
            'preview': self.thumbnail,
            'stream_type': self.stream_type,
            'viewers': self.viewers
        }


class Community(Base):
    __tablename__  = 'communities'
    id = Column(Integer, primary_key=True)
    twitch_name = Column(Unicode(64), unique=True)
    url = Column(Unicode(1024), unique=True)
    display_name = Column(Unicode(256), unique=True)
    active = Column(Boolean, default=1)
    last_update = Column(DateTime)
    default = Column(Boolean, default=0)
    streams = relationship('Stream', back_populates='community')

    def __init__(self, twitch_name, display_name, url, active=True):
        self.twitch_name = twitch_name
        self.url = url
        self.display_name = display_name
        self.active = active
