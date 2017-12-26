import { Site } from '../Site';
import { SiteOptions } from '../../typings';

class TemplateSite extends Site {
  public config(): SiteOptions {
    return {
      name: '',
      url: '',
      favicon: '',
      entryPoint: '',
      selectors: {
        previousPage: '',
        video: {
          url: '',
          title: '',
          duration: '',
          thumbnailUrl: '',
        },
        videoDetails: {
          tags: '',
        },
      },
    };
  }
}

export { TemplateSite };
