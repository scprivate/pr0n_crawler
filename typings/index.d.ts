interface SiteFields {
  previousPage: {
    selector: string,
    normalizer?(previousPage: string): string
  }

  videosUrl: {
    selector: string,
    normalizer?(urls: Array<string>): Array<string>
  }

  videosThumbnailUrl: {
    selector: string,
    normalizer?(thumbnailUrls: Array<string>): Array<string>
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
    tags: {
      selector: string,
      normalizer?(tags: Array<string>): Array<string>
    }
  }
}
