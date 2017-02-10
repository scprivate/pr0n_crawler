import asyncio
import logging
import time
from typing import Dict, List

import aiohttp
from inflection import humanize, parameterize
from lxml import html

from src.models import Video, Site, Tag, VideoToTag


class CrawlerMixin(object):
    site_name = None
    site_url = None
    crawler_entry_point = None
    crawler_selectors = None
    crawler_max_videos = 9000

    already_existing_videos_count = 0

    def __init__(self):
        self.crawler_current_videos = 0
        self._hydrate_logger()
        self.logger.debug('__init__()')

        self.site, created = Site.get_or_create(
            name=self.site_name,
            url=self.site_url
        )

        if created:
            self.logger.info('Site created.')

    async def crawl(self, url=None, retry=20):
        if not url:
            url = self.site_url + self.crawler_entry_point

        if self.crawler_current_videos >= self.crawler_max_videos:
            self.logger.info('Max videos number reached, end.')
            return

        prev_already_existing_videos_count = self.already_existing_videos_count

        # 1: download videos page
        [content, tree] = await self._download_videos_page(url)

        # 2: find videos from previously downloaded page
        self.logger.info('Finding videos metadata from {}...'.format(url))
        time_start = time.time()
        videos = await self._find_videos_from_videos_page(tree)
        time_end = time.time()
        self.logger.info('Found videos metadata for {} videos in {:.3f} seconds.'.format(
            len(videos),
            time_end - time_start)
        )

        # 3: find next page url from previously downloaded page
        next_page = find_next_page(tree, self.next_page_selector)

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
            self.logger.info('-' * 60)

            if self.already_existing_videos_count == prev_already_existing_videos_count:
                self.logger.info('0 videos were created from last crawl, now exiting...')
                return

            url = self.site_url + next_page
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
                    content = await response.text()
                    tree = html.fromstring(content)
                    return [content, tree]

    async def _find_videos_from_videos_page(self, tree):
        videos_metadata = self._find_videos_metadata(tree)
        videos = self._get_or_create_videos_from_metadata(videos_metadata)
        await self._find_more_videos_metadata(videos)

        return videos

    def _find_videos_metadata(self, tree) -> [list]:
        titles = find_videos_title(tree, self.video_title_selector)
        urls = find_videos_url(tree, self.video_url_selector)
        thumbnail_urls = find_videos_thumbnail_url(tree, self.video_thumbnail_url_selector)

        durations = find_videos_duration(tree, self.video_duration_selector)
        durations = [self.crawl_convert_video_duration_to_seconds(d) for d in durations]

        return list(zip(titles, durations, urls, thumbnail_urls))

    async def _find_more_videos_metadata(self, videos: List[Video]):
        tasks = []

        for video in videos:
            tasks.append(self._download_video_page(video))

        await asyncio.gather(*tasks)

    async def _download_video_page(self, video: Video):
        url = self.site_url + video.url
        self.logger.info('Downloading {}...'.format(url))

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    self.logger.warning('Can not download {}'.format(url))
                    return

                content = await response.text()
                self.logger.info('Downloaded {}.'.format(url))
                tree = html.fromstring(content)

                details = find_video_details(tree, dict(
                    video_details_tags=self.video_details_tags_selector
                ))

                save_video_details(video, details)

                self.logger.info('Got details from {}'.format(url))
                self.crawler_current_videos += 1
                self._hydrate_logger()

    def _get_or_create_videos_from_metadata(self, videos_metadata):
        videos = []

        for m in videos_metadata:
            video, created = Video.get_or_create(
                title=m[0].strip(),
                duration=m[1],
                url=m[2].strip(),
                thumbnail_url=m[3].strip(),
                site=self.site
            )
            videos.append(video)

            if created:
                self.already_existing_videos_count += 1

        return videos

    @property
    def video_title_selector(self):
        return self.crawler_selectors.get('video').get('title')

    @property
    def video_duration_selector(self):
        return self.crawler_selectors.get('video').get('duration')

    @property
    def video_url_selector(self):
        return self.crawler_selectors.get('video').get('url')

    @property
    def video_thumbnail_url_selector(self):
        return self.crawler_selectors.get('video').get('thumbnail_url')

    @property
    def video_details_tags_selector(self):
        return self.crawler_selectors.get('video_details').get('tags')

    @property
    def next_page_selector(self):
        return self.crawler_selectors.get('next_page')


def find_videos_title(tree, video_title_selector) -> [str]:
    return tree.xpath(video_title_selector)


def find_videos_duration(tree, video_duration_selector) -> [int]:
    return tree.xpath(video_duration_selector)


def find_videos_url(tree, video_url_selector) -> [str]:
    return tree.xpath(video_url_selector)


def find_videos_thumbnail_url(tree, video_thumbnail_url_selector) -> [str]:
    return tree.xpath(video_thumbnail_url_selector)


def find_video_details(tree, selectors: Dict[str, str]) -> Dict[str, list]:
    return dict(
        tags=tree.xpath(selectors.get('video_details_tags'))
    )


def find_next_page(tree, next_page_selector: str) -> str:
    return tree.xpath(next_page_selector)[0]


def save_video_details(video: Video, details: Dict):
    for found_tag in details.get('tags'):
        slug = parameterize(found_tag.strip())
        tag = humanize(slug)

        if not slug:
            continue

        tag, created = Tag.get_or_create(
            tag=tag,
            slug=slug
        )

        VideoToTag.get_or_create(video=video, tag=tag)
