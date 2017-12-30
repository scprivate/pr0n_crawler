import { Site } from './Site';

class Extractor {
  constructor(private site: Site, private content: string) {
  }

  public extractPreviousPage() {
    const { selector, normalizer } = this.site.getFields().previousPage;

  }

  public extractVideosUrl() {
    const { selector, normalizer } = this.site.getFields().previousPage;

  }

  public extractVideosThumbnailUrl() {
    const { selector, normalizer } = this.site.getFields().previousPage;

  }
}

export {
  Extractor,
};
