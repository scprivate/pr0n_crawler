#!/usr/bin/env python
import asyncio
import logging
import sys

from colorlog import ColoredFormatter

from src.crawlers.youjizz import YoujizzCrawler
from src.models import db, Site, Video, Tag, VideoToTag


def create_logger() -> logging.Logger:
    root = logging.getLogger('pr0n_crawler')
    root.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)

    ch.setFormatter(ColoredFormatter(
        '[%(log_color)s%(levelname)s %(reset)s] %(bold)s%(site_name)s%(reset)s'
        ' (%(videos_current_number)s/%(videos_max_number)s) : %(message)s'
    ))

    root.addHandler(ch)
    return root


if __name__ == '__main__':
    db.connect()
    db.create_tables([Site, Video, Tag, VideoToTag], safe=True)
    logger = create_logger()

    crawlers = [
        YoujizzCrawler(),
    ]

    loop = asyncio.get_event_loop()

    try:
        tasks = [crawler.crawl() for crawler in crawlers]
        loop.run_until_complete(asyncio.wait(tasks))
    except KeyboardInterrupt:
        loop.close()
