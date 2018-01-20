import { NormalizedCacheObject } from 'apollo-cache-inmemory';
import { ApolloClient } from 'apollo-client';
import { Site } from './Site';

class Crawler {
  private crawledPages: number;
  private crawledVideos: number;

  constructor(private client: ApolloClient<NormalizedCacheObject>, private site: Site) {
    this.crawledPages = 0;
    this.crawledVideos = 0;
  }

  public crawl(url: string = this.site.getEntryPoint()) {}
}

export { Crawler };
