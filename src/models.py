from playhouse.fields import ManyToManyField, Model, CharField, ForeignKeyField, IntegerField, MySQLDatabase

from config import DATABASE

__all__ = [
    'db',
    'Site',
    'Video',
    'Tag',
    'VideoTag'
]

db = MySQLDatabase(
    host=DATABASE['HOST'],
    database=DATABASE['DATABASE'],
    charset=DATABASE['CHARSET'],
    user=DATABASE['USER'],
    password=DATABASE['PASSWORD']
)

db.execute_sql("SET NAMES %s COLLATE %s;", (
    DATABASE['CHARSET'], DATABASE['COLLATION']
))


class Site(Model):
    name = CharField()
    url = CharField()

    class Meta:
        database = db
        db_table = 'sites'


class Tag(Model):
    tag = CharField()
    slug = CharField()

    class Meta:
        database = db
        db_table = 'tags'


class Video(Model):
    title = CharField()
    duration = IntegerField()
    url = CharField()
    thumbnail_url = CharField()

    site = ForeignKeyField(Site)
    tags = ManyToManyField(Tag, related_name="videos")

    class Meta:
        database = db
        db_table = 'videos'


VideoTag = Tag.videos.get_through_model()
