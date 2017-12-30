interface ISiteFields {
  previousPage: {
    selector: string,
    normalizer?(previousPage: string): string,
  };

  videosUrl: {
    selector: string,
    normalizer?(urls: string[]): string[],
  };

  videosThumbnailUrl: {
    selector: string,
    normalizer?(thumbnailUrls: string[]): string[],
  };

  video: {
    title: {
      selector: string,
      normalizer?(title: string): string,
    }
    duration: {
      selector: string,
      normalizer?(duration: string): number,
    }
    tags: {
      selector: string,
      normalizer?(tags: string[]): string[],
    },
  };
}
