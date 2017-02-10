import os

from peewee import *
from playhouse.fields import ManyToManyField
from playhouse.sqlite_ext import SqliteExtDatabase

__all__ = [
    'db',
    'Site',
    'Video',
    'Tag',
    'VideoToTag'
]

db = SqliteExtDatabase(
    os.path.join(os.path.dirname('..'), 'database.sqlite')
)


class BaseModel(Model):
    class Meta:
        database = db


class Site(BaseModel):
    name = CharField()
    url = CharField()


class Tag(BaseModel):
    tag = CharField()
    slug = CharField()


class Video(BaseModel):
    title = CharField()
    duration = IntegerField()
    url = CharField()
    thumbnail_url = CharField()

    site = ForeignKeyField(Site)
    tags = ManyToManyField(Tag, related_name="videos")


VideoToTag = Tag.videos.get_through_model()
