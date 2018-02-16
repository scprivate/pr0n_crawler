import * as sec from 'sec';
import { Site } from '../Site';
import { resolve as resolveUrl } from 'url';

class YouJizzSite extends Site {
  public getUrl(): string {
    return 'https://www.youjizz.com';
  }

  public getName(): string {
    return 'YouJizz';
  }

  public getFavicon(): string {
    return 'https://www.youjizz.com/favicon.ico';
  }

  public getEntryPoint(): string {
    return 'https://www.youjizz.com/newest-clips/2.html';
  }

  public getFields(): ISiteFields {
    return {
      previousPage: {
        selector:
          '(//*[contains(@class, "pagination")]/li[contains(@class, "active")]/preceding-sibling::li/a/@href)[last()]',
        normalizer: (previousPage: string) => String(resolveUrl(this.getUrl(), previousPage)),
      },
      videosUrl: {
        selector: '//*[contains(@class, "video-title")]/a/@href',
        normalizer: (urls: string[]) => urls.map(url => String(resolveUrl(this.getUrl(), url))),
      },
      videosThumbnailUrl: {
        selector: '//*[contains(@class, "video-item")]/div/a/img[contains(@class, "img-responsive")]/@data-original',
        normalizer: (thumbnailsUrl: string[]) => thumbnailsUrl.map(url => String(resolveUrl(this.getUrl(), url))),
      },
      video: {
        title: {
          selector: '//title/text()',
        },
        duration: {
          selector: '(//*[contains(@class, "video-info")]/div[3]/text())[last()]',
          normalizer: (duration: string) => sec(duration),
        },
        tags: {
          selector: '(//*[contains(@class, "tag-links")])[last()]/ul/li[contains(@class, "red-li")]/a/text()',
        },
      },
    };
  }
}

export { YouJizzSite };
