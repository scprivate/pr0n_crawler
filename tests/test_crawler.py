from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from peewee import SqliteDatabase
from playhouse.test_utils import test_database

from src.crawlermixin import CrawlerMixin
from src.crawlers.youjizz import YoujizzCrawler
from src.models import Site, Video, Tag, VideoTag

# set-up database #

test_db = SqliteDatabase(':memory:')


def with_test_database(fnc):
    def wrapper(*args):
        with test_database(test_db, (Site, Video, Tag, VideoTag)):
            fnc(*args)

    return wrapper


# setup fake web pron site #

class FakeCrawler(CrawlerMixin):
    site_url = 'http://localhost'
    site_name = 'Fake'
    crawler_entry_point = '/'
    crawler_selectors = dict(
        next_page='//*[@id="pagination"]/[@class=current]/following-sibling::a/@href[1]',

        video=dict(
            title='//*[@class="video__title"]/text()',
            duration='//*[@class="video__duration"]/text()',
            url='//*[@class="video"]/a/@href',
            thumbnail_url='//[@class="video"]/a/img/@src',
        ),

        video_details=dict(
            tags='//*[@id="tags1"]/a/text()',
        )
    )


def web_entry_point():
    return web.Response(text="""
<!DOCTYPE html>
    <html>
    <head></head>
    <body>
        <div id="videos">
            <div class="video">
                <a href="/video/first_title">
                    <img src="/thumbnail/first_title.jpg" />
                    <span class="video__duration">13:37</span>
                    <span class="video__title">First title</span>
                </a>
                <a href="/video/second_title">
                    <img src="/thumbnail/second_title.jpg" />
                    <span class="video__duration">12:34</span>
                    <span class="video__title">Second title</span>
                </a>
                <a href="/video/third_title">
                    <img src="/thumbnail/third_title.jpg" />
                    <span class="video__duration">2:23</span>
                    <span class="video__title">Third title</span>
                </a>
            </div>
        </div>
        <div id="pagination">
            <a class="current" href="/">Page 1</a>
            <a href="/?page=2">Page 2</a>
            <a href="/?page=3">Page 3</a>
        </div>
    </body>
    </html>
""")


class TestCrawler(AioHTTPTestCase):
    async def get_application(self, loop):
        app = web.Application(loop=loop)
        app.router.add_get('/', web_entry_point)

        return app

    def test_empty_site_name_and_url(self):
        class Crawler(CrawlerMixin):
            pass

        with self.assertRaises(ValueError):
            Crawler()

    @with_test_database
    def test_empty_selectors(self):
        class Crawler(CrawlerMixin):
            site_name = 'My site'
            site_url = 'https://example.com'

        crawler = Crawler()

        with self.assertRaises(AttributeError):
            print(crawler.video_title_selector)

        with self.assertRaises(AttributeError):
            print(crawler.video_duration_selector)

        with self.assertRaises(AttributeError):
            print(crawler.video_url_selector)

        with self.assertRaises(AttributeError):
            print(crawler.video_thumbnail_url_selector)

        with self.assertRaises(AttributeError):
            print(crawler.video_details_tags_selector)

        self.assertIsNone(crawler.next_page_selector)

    @with_test_database
    def test_non_empty_selectors(self):
        youjizz_crawler = YoujizzCrawler()
        self.assertEqual(youjizz_crawler.video_title_selector, '//*[@id="title1"]/text()')
        self.assertEqual(youjizz_crawler.video_duration_selector, '//*[@id="title2"]/span[1]/span/text()')
        self.assertEqual(youjizz_crawler.video_url_selector, '//*[@id="min"]/a/@href')
        self.assertEqual(youjizz_crawler.video_thumbnail_url_selector,
                         '//*[@id="min"]/img[@class="lazy"]/@data-original')
        self.assertEqual(youjizz_crawler.video_details_tags_selector,
                         '//*[@id="tags1"]/a/text()')
        self.assertEqual(youjizz_crawler.next_page_selector,
                         '//*[@id="pagination"]/span/following-sibling::a/@href[1]')

    @with_test_database
    @unittest_run_loop
    async def test_find_videos_metadata(self):
        self.skipTest('Not completed')

        # fake_crawler = FakeCrawler()
        # request = await self.client.request('GET', '/')
        # text = await request.text()
