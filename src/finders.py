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


def find_prev_page(tree, prev_page_selector):
    """
    :type tree: lxml.html.Element
    :type prev_page_selector: str
    :rtype: str
    """

    return tree.xpath(prev_page_selector)[0]
