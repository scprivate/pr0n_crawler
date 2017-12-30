import { Site } from '../Site';

class TemplateSite extends Site {
  public getUrl(): string {
    return 'https://www.template.com';
  }

  public getName(): string {
    return 'Template';
  }

  public getFavicon(): string {
    return 'https://www.template.com/favicon.ico';
  }

  public getEntryPoint(): string {
    return 'https://www.template.com/last/100.html';
  }

  public getFields(): SiteFields {
    return {
      previousPage: {
        selector: '',
        normalizer: (previousPage: string) => previousPage,
      },
      videosUrl: {
        selector: '',
        normalizer: (urls: Array<string>) => urls,
      },
      videosThumbnailUrl: {
        selector: '',
        normalizer: (thumbnailsUrl: Array<string>) => thumbnailsUrl,
      },
      video: {
        title: {
          selector: '',
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

export { TemplateSite };
