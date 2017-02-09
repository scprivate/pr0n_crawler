import os

from inflection import pluralize, parameterize
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

db = SqliteExtDatabase(os.path.join(os.path.dirname('..'), 'database.sqlite'))


def normalize_model_name(name):
    return parameterize(pluralize(name))


class BaseModel(Model):
    class Meta:
        database = db
        db_table_func = lambda model: normalize_model_name(model.__name__)


class Site(BaseModel):
    db_column = 'sites'

    name = CharField()
    url = CharField()


class Tag(BaseModel):
    db_column = 'tags'

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
