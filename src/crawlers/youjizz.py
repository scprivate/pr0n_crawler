from src import helpers
from src.crawlermixin import CrawlerMixin


class YoujizzCrawler(CrawlerMixin):
    site_name = 'Youjizz'
    site_url = 'https://www.youjizz.com'
    site_favicon_url = site_url + '/favicon.ico'

    crawler_entry_point = '/newest-clips/300.html'
    crawler_selectors = dict(
        prev_page='(//*[@id="pagination"]/span/preceding-sibling::a/@href)[last()]',

        video=dict(
            title='//*[contains(@class, "video-title")]/a/text()',
            duration='//*[contains(@class, "time")]/text()',
            url='//*[contains(@class, "video-title")]/a/@href',
            thumbnail_url='//a[@class="frame"]/img[contains(@class, "lazy")]/@data-original',
        ),

        video_details=dict(
            tags='//*[contains(@class, "tag-links desktop-only")]/ul/li/a/text()',
        )
    )

    def crawl_convert_video_duration_to_seconds(self, duration):
        if not duration or duration == 'N/A' or duration == 'None':
            return 0

        return helpers.hms_to_s(duration)
