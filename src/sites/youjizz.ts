import { Site } from '../Site';

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
    return 'https://www.youjizz.com/newest-clips/100.html';
  }

  public getFields(): SiteFields {
    return {
      previousPage: {
        selector: '(//ul[contains(@class, "pagination")]/li[contains(@class, "active")]/a/@href)[last()]',
        normalizer: (previousPage: string) => String(new URL(previousPage, this.getUrl())),
      },
      videosUrl: {
        selector: '//*[contains(@class, "video-title")]/a/@href',
        normalizer: (urls: Array<string>) => urls.map(url => String(new URL(url, this.getUrl()))),
      },
      videosThumbnailUrl: {
        selector: '',
        normalizer: (thumbnailsUrl: Array<string>) => thumbnailsUrl,
      },
      video: {
        title: {
          selector: '//*[contains(@class, "video-player")]/following-sibling::h3/text()',
          normalizer: (title: string) => title,
        },
        duration: {
          selector: '',
          normalizer: (duration: string) => Number(duration),
        },
        tags: {
          selector: '',
          normalizer: (tags: Array<string>) => tags,
        },
      },
    };
  }
}

export { YouJizzSite };
