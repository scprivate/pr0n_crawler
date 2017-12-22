export interface SiteOptions {
  name: string;
  url: string;
  favicon: string;
  entryPoint: string;
  selectors: CrawlerSelectors;
}

interface CrawlerSelectors {
  previousPage: string;
  video: {
    title: string;
    duration: string;
    url: string;
    thumbnailUrl: string;
  }
  videoDetails: {
    tags: string;
  }
}
