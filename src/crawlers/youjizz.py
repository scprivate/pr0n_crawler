from src import helpers
from src.crawlermixin import CrawlerMixin


class YoujizzCrawler(CrawlerMixin):
    site_name = 'Youjizz'
    site_url = 'https://www.youjizz.com'
    site_favicon_url = site_url + '/favicon.ico'

    crawler_entry_point = '/page/1.html'
    crawler_max_videos = 150
    crawler_selectors = dict(
        next_page='//*[@id="pagination"]/span/following-sibling::a[1]/@href',

        video=dict(
            title='//*[@id="title1"]/text()',
            duration='//*[@id="title2"]/span[1]/span/text()',
            video_url='//*[@id="min"]/a/@href',
            thumbnail_url='//*[@id="min"]/img[@class="lazy"]/@data-original',
        ),

        video_details=dict(
            tags='//*[@id="tags1"]/a/text()',
        )
    )

    def crawl_convert_video_duration_to_seconds(self, duration: str):
        if duration == 'N/A':
            return 0

        return helpers.hms_to_s(duration)
