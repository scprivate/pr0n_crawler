import { Site } from '../Site';
import { SiteOptions } from '../../typings';

class TemplateSite extends Site {
  public config(): SiteOptions {
    return {
      name: 'Template',
      url: 'https://www.template.com',
      favicon: 'https://www.template.com/favicon.ico',
      entryPoint: 'https://www.template.com/last/100.html',
      fields: {
        previousPage: {
          selector: '',
          normalizer: (previousPage: string) => previousPage,
        },
        videosUrl: {
          selector: '',
          normalizer: (urls: Array<string>) => urls,
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
          thumbnailUrl: {
            selector: '',
            normalizer: (thumbnailUrl: string) => thumbnailUrl,
          },
          tags: {
            selector: '',
            normalizer: (tags: Array<string>) => tags,
          },
        },
      },
    };
  }
}

export { TemplateSite };
