import { SiteOptions } from '../typings';

abstract class Site {
  abstract config(): SiteOptions
}

export { Site };
