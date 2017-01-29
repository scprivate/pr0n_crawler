import asyncio
import logging
import time

import aiohttp
from inflection import humanize, parameterize
from lxml import html

from src.models import Video, Site, Tag, VideoToTag


class CrawlerMixin(object):
    site_name = None
    site_url = None
    crawler_entry_point = None
    crawler_selectors = None
    crawler_max_videos = 100

    def __init__(self):
        self.crawler_current_videos = 0
        self._hydrate_logger()
        self.logger.debug('__init__()')

        self.site, created = Site.get_or_create(name=self.site_name, url=self.site_url)
        if created:
            self.logger.info('Site created.')

    async def crawl(self, url=None, retry=20):
        self.logger.debug('crawl()')

        if not url:
            url = self.site_url + self.crawler_entry_point

        if self.crawler_current_videos >= self.crawler_max_videos:
            self.logger.info('Max videos number reached, end.')
            return

        [videos, next_page] = await self._download_videos_page(url)

        if not videos or len(videos) == 0:
            if retry == 0:
                self.logger.critical("Can't find videos from {}, after 20 try.".format(url))
                exit(1)

            delay = (20 - retry) ** 1.5 + 10
            retry -= 1
            self.logger.warning('Found 0 videos on {}, {} try left, waiting {} seconds...'.format(url, retry, delay))
            await asyncio.sleep(delay)
            await self.crawl(url, retry)
        else:
            url = self.site_url + next_page
            self.logger.info('-' * 60)

            await self.crawl(url)

    async def crawl_convert_video_duration_to_seconds(self, duration: str):
        raise NotImplementedError

    def _hydrate_logger(self):
        self.logger = logging.LoggerAdapter(logging.getLogger('pr0n_crawler'), {
            'site_name': self.site_name,
            'videos_current_number': self.crawler_current_videos,
            'videos_max_number': self.crawler_max_videos,
        })

    async def _download_videos_page(self, url):
        self.logger.debug('_download_videos_page()')
        self.logger.info('Downloading {}...'.format(url))

        time_start = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    self.logger.error('Can not download {}, got 404.'.format(url))
                    exit(1)
                else:
                    self.logger.info('Downloaded in {:.3f} seconds.'.format(time.time() - time_start))
                    return await self._parse_videos_page_response(response)

    async def _download_video_page_and_find_details(self, videos: [Video, bool]) -> [Video]:
        self.logger.debug('_fetch_videos_details()')

        tasks = []

        for [video, _] in videos:
            tasks.append(self._download_video_page(video))

        return await asyncio.gather(*tasks)

    async def _download_video_page(self, video: Video):
        url = self.site_url + video.url

        self.logger.debug('Download details for {}.'.format(video.url))

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    self.logger.warning('Can not download {}'.format(url))
                else:
                    details = await self._find_video_details(response)

                    self.logger.debug('Got details for {}.'.format(video.url))

                    for found_tag in details.get('tags'):
                        tag, created = Tag.get_or_create(
                            tag=humanize(found_tag.strip()),
                            slug=parameterize(found_tag.strip())
                        )

                        # It's better than video.tags.add(tag), because it wont
                        # raises à peewee.IntegrityError if relation between
                        # Video and Tag already exists.
                        VideoToTag.get_or_create(video=video, tag=tag)

                    self.logger.debug('Saved {} in database')
                    self.crawler_current_videos += 1
                    self._hydrate_logger()

            return video

    async def _parse_videos_page_response(self, response):
        content = await response.text()
        tree = html.fromstring(content)

        return [
            await self._find_videos_from_videos_page(response, tree),
            await self._find_next_page(response, tree),
        ]

    async def _find_videos_from_videos_page(self, response, tree):
        self.logger.debug('_find_videos_from_videos_page()')

        # 1: find videos
        time_start = time.time()
        self.logger.info('Finding videos from {}...'.format(response.url))
        videos = await self._find_videos_metadata(tree)
        self.logger.info('Found {} videos in {:.3f} seconds.'.format(len(videos), time.time() - time_start))

        # 2: find videos details
        time_start = time.time()
        self.logger.info('Finding details for {} videos.'.format(len(videos)))
        videos = await self._download_video_page_and_find_details(videos)
        time_end = time.time()
        self.logger.info('Found details for {} videos in {:.3f} seconds.'.format(len(videos), time_end - time_start))

        return videos

    async def _find_videos_metadata(self, tree) -> [dict]:
        self.logger.debug('_find_videos()')

        # Faster than asyncio.gather(...)
        videos_metadata = zip(
            await self._find_videos_titles(tree),
            await self._find_videos_duration(tree),
            await self._find_videos_url(tree),
            await self._find_videos_thumbnail_url(tree),
        )

        # tasks = [
        #     self._find_videos_titles(tree),
        #     self._find_videos_duration(tree),
        #     self._find_videos_url(tree),
        #     self._find_videos_thumbnail_url(tree),
        # ]
        #
        # metadatas = await asyncio.gather(*tasks)
        # metadatas = [list(t) for t in zip(*metadatas)]

        return [
            Video.get_or_create(
                title=videos_metadata[0].strip(), duration=videos_metadata[1],
                url=videos_metadata[2].strip(), thumbnail_url=videos_metadata[3].strip(),
                site=self.site
            )
            for videos_metadata in videos_metadata
            ]

    async def _find_video_details(self, response):
        content = await response.text()
        tree = html.fromstring(content)

        video_details_selectors = self.crawler_selectors.get('video_details')

        return dict(
            tags=tree.xpath(video_details_selectors.get('tags'))
        )

    async def _find_next_page(self, response, tree):
        self.logger.debug('_find_next_page_url()')

        try:
            next_page = tree.xpath(self.crawler_selectors.get('next_page'))[0]
            return next_page
        except IndexError as e:
            self.logger.critical('Error when trying to get next page: {}'.format(e))

    async def _find_videos_titles(self, tree) -> [str]:
        self.logger.debug('_find_videos_titles()')

        return tree.xpath(self.crawler_selectors.get('video').get('title'))

    async def _find_videos_duration(self, tree) -> [int]:
        self.logger.debug('_find_videos_duration()')

        durations = tree.xpath(self.crawler_selectors.get('video').get('duration'))
        return [self.crawl_convert_video_duration_to_seconds(duration) for duration in durations]

    async def _find_videos_url(self, tree) -> [str]:
        self.logger.debug('_find_videos_url()')

        return tree.xpath(self.crawler_selectors.get('video').get('video_url'))

    async def _find_videos_thumbnail_url(self, tree) -> [str]:
        self.logger.debug('_find_videos_thumbnail_url()')

        return tree.xpath(self.crawler_selectors.get('video').get('thumbnail_url'))
