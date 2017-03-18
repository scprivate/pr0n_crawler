import asyncio
import logging
import time

import aiohttp
from inflection import humanize, parameterize
from lxml import html
from tenacity import before_log, retry, stop_after_attempt, wait_random

from src.models import Video, Site, Tag, VideoTag


class CrawlerMixin(object):
    site_name = None  # type: str
    site_url = None  # type: str
    crawler_entry_point = None  # type: str
    crawler_selectors = dict()  # type: dict[str, str | dict[str, str]]
    crawler_max_videos = 9000

    already_existing_videos_count = 0

    def __init__(self):
        self.crawler_current_videos = 0
        self._hydrate_logger()

        if not (self.site_name or self.site_url):
            raise ValueError("Site's name and site's url should not be None.")

        self.site, created = Site.get_or_create(
            name=self.site_name,
            url=self.site_url
        )

        if created:
            self.logger.info('Site created.')

    @retry(
        stop=stop_after_attempt(20), wait=wait_random(8, 512),
        before=before_log(logging.getLogger(), logging.WARN)
    )
    async def crawl(self, url=None):
        """
        :type url: str
        :return:
        """

        if not url:
            url = self.site_url + self.crawler_entry_point

        if self.crawler_current_videos >= self.crawler_max_videos:
            self.logger.info('Max videos number reached, end.')
            return

        prev_already_existing_videos_count = self.already_existing_videos_count

        # 1: download videos page
        [_, tree] = await self._download_videos_page(url)

        # 2: find videos from previously downloaded page
        self.logger.info('Finding videos metadata from {}...'.format(url))
        time_start = time.time()
        videos = await self._find_videos_from_videos_page(tree)
        time_end = time.time()

        self.logger.info(
            'Found videos metadata for {} videos in {:.3f} seconds.'.format(
                len(videos),
                time_end - time_start)
        )

        # 3: check if there is videos
        if not videos:
            raise ValueError('No videos found')

        # 4: find next page url from previously downloaded page
        next_page = find_next_page(tree, self.next_page_selector)

        self.logger.info('-' * 60)

        if self.already_existing_videos_count == prev_already_existing_videos_count:
            self.logger.info('0 videos were created from last crawl, now exiting...')
            return

        url = self.site_url + next_page
        await self.crawl(url)

    async def crawl_convert_video_duration_to_seconds(self, duration):
        """
        :type duration: str
        :rtype: int
        """

        raise NotImplementedError

    def _hydrate_logger(self):
        self.logger = logging.LoggerAdapter(logging.getLogger('pr0n_crawler'), {
            'site_name': self.site_name,
            'videos_current_number': self.crawler_current_videos,
            'videos_max_number': self.crawler_max_videos,
        })

    async def _download_videos_page(self, url):
        """
        :type url: str
        :rtype: list[str, lxml.html.Element]
        """

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
        """
        :type tree: lxml.html.Element
        :rtype: list[Video]
        """

        videos_metadata = self._fetch_videos_page_and_find_metadata(tree)
        videos = self._get_or_create_videos_from_metadata(videos_metadata)
        await self._find_more_videos_metadata(videos)

        return videos

    def _fetch_videos_page_and_find_metadata(self, tree):
        """
        :param tree: lxml.html.Element
        :return: list of tuples following (title, url, thumbnail_url, durations) format
        :rtype: list[(str, str, str, int)]
        """

        titles = find_videos_title(tree, self.video_title_selector)
        urls = find_videos_url(tree, self.video_url_selector)
        thumbnail_urls = find_videos_thumbnail_url(tree, self.video_thumbnail_url_selector)
        durations = map(
            self.crawl_convert_video_duration_to_seconds,
            find_videos_duration(tree, self.video_duration_selector)
        )

        return list(zip(titles, urls, thumbnail_urls, durations))

    def _get_or_create_videos_from_metadata(self, videos_metadata):
        """
        :type videos_metadata: list[(str, str, str, int)]
        :rtype: list[Video]
        """
        videos = []

        for m in videos_metadata:
            video, created = Video.get_or_create(
                title=m[0].strip(),
                url=m[1].strip(),
                thumbnail_url=m[2].strip(),
                duration=m[3],
                site=self.site
            )
            videos.append(video)

            if created:
                self.already_existing_videos_count += 1

        return videos

    async def _find_more_videos_metadata(self, videos):
        """
        :param videos: list[Video]
        """

        tasks = []

        for video in videos:
            tasks.append(self._fetch_video_page_and_find_metadata(video))

        await asyncio.gather(*tasks)

    @retry(
        stop=stop_after_attempt(20), wait=wait_random(8, 512),
        before=before_log(logging.getLogger(), logging.WARN)
    )
    async def _fetch_video_page_and_find_metadata(self, video):
        """
        :type video: Video
        """

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

    @property
    def video_title_selector(self):
        """
        :rtype: str
        """
        return self.crawler_selectors.get('video').get('title')

    @property
    def video_duration_selector(self):
        """
        :rtype: str
        """
        return self.crawler_selectors.get('video').get('duration')

    @property
    def video_url_selector(self):
        """
        :rtype: str
        """
        return self.crawler_selectors.get('video').get('url')

    @property
    def video_thumbnail_url_selector(self):
        """
        :rtype: str
        """
        return self.crawler_selectors.get('video').get('thumbnail_url')

    @property
    def video_details_tags_selector(self):
        """
        :rtype: str
        """
        return self.crawler_selectors.get('video_details').get('tags')

    @property
    def next_page_selector(self):
        """
        :rtype: str
        """
        return self.crawler_selectors.get('next_page')


def find_videos_title(tree, video_title_selector):
    """
    :type tree: lxml.html.Element
    :type video_title_selector: str
    :rtype: list[str]
    """

    return tree.xpath(video_title_selector)


def find_videos_duration(tree, video_duration_selector):
    """
    :type tree: lxml.html.Element
    :type video_duration_selector: str
    :rtype: list[str]
    """

    return tree.xpath(video_duration_selector)


def find_videos_url(tree, video_url_selector):
    """
    :type tree: lxml.html.Element
    :type video_url_selector: str
    :rtype: list[str]
    """

    return tree.xpath(video_url_selector)


def find_videos_thumbnail_url(tree, video_thumbnail_url_selector):
    """
    :type tree: lxml.html.Element
    :type video_thumbnail_url_selector: str
    :rtype: list[str]
    """

    return tree.xpath(video_thumbnail_url_selector)


def find_video_details(tree, selectors):
    """
    :type tree: lxml.html.Element
    :type selectors: dict[str, str]
    :rtype: dict[str, list]
    """

    return dict(
        tags=tree.xpath(selectors.get('video_details_tags'))
    )


def find_next_page(tree, next_page_selector):
    """
    :type tree: lxml.html.Element
    :type next_page_selector: str
    :rtype: str
    """

    return tree.xpath(next_page_selector)[0]


def save_video_details(video, details):
    """
    :type video: Video
    :type details: dict
    """

    for found_tag in details.get('tags'):
        slug = parameterize(found_tag.strip())
        tag = humanize(slug)

        if not slug:
            continue

        tag, created = Tag.get_or_create(
            tag=tag,
            slug=slug
        )

        VideoTag.get_or_create(video=video, tag=tag)
