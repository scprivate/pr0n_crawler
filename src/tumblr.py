import pytumblr

from config import TUMBLR

client = pytumblr.TumblrRestClient(
    TUMBLR.get('CONSUMER_KEY'),
    TUMBLR.get('CONSUMER_SECRET'),
    TUMBLR.get('OAUTH_TOKEN'),
    TUMBLR.get('OAUTH_SECRET'),
)


def post(video):
    """
    :type video: models.Video
    :return: 
    """

    title = video.title
    url = video.url  # type: str
    image_url = video.thumbnail_url  # type: str
    tags = [tag.tag for tag in video.tags]

    if not url.startswith('http'):
        url = video.site.url + '/' + url

    if not image_url.startswith('http'):
        image_url = video.site.url + '/' + image_url

    client.create_photo(
        TUMBLR.get('DOMAIN'),
        state='queue', tweet=title,
        source=image_url, link=url,
        tags=tags
    )
