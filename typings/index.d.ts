export interface SiteOptions {
  name: string;
  url: string;
  favicon: string;
  entryPoint: string;
  fields: SiteOptionsFields
}

interface SiteOptionsFields {
  previousPage: {
    selector: string,
    normalizer?(previousPage: string): string
  }

  videosUrl: {
    selector: string,
    normalizer?(urls: Array<string>): Array<string>
  }

  video: {
    title: {
      selector: string,
      normalizer?(title: string): string
    }
    duration: {
      selector: string,
      normalizer?(duration: string): Number
    }
    thumbnailUrl: {
      selector: string,
      normalizer?(thumbnailUrl: string): string
    }
    tags: {
      selector: string,
      normalizer?(tags: Array<string>): Array<string>
    }
  }
}
