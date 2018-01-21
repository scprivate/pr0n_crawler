import { NormalizedCacheObject } from 'apollo-cache-inmemory';
import { ApolloClient } from 'apollo-client';
import { Video } from './entities/Video';
import { Extractor } from './Extractor';
import { Site } from './Site';

import axios from 'axios';
import { zip } from 'zip-array';
import { Site as SiteEntity } from './entities/Site';
import ExtractorNoPreviousPageFoundError from './errors/ExtractorNoPreviousPageFoundError';

class Crawler {
  private crawledPages: number;
  private crawledVideos: number;

  constructor(private client: ApolloClient<NormalizedCacheObject>, private site: Site) {
    this.crawledPages = 0;
    this.crawledVideos = 0;
  }

  public async crawl(url: string = this.site.getEntryPoint()) {
    console.log(`Fetching ${url}...`);

    const extractor = new Extractor(this.site, (await axios(url)).data);
    const videos: Video[] = this.initVideos(extractor);

    await Promise.all(
      videos.map(async video => {
        const response = await axios(video.url);
        this.handleVideo(video, response.data);
        this.crawledVideos += 1;
      })
    );

    this.crawledPages += 1;
    console.log(`Fetching ${url}: done.`);

    try {
      const previousPage = extractor.extractPreviousPage();
      this.crawl(previousPage);
    } catch (e) {
      if (e instanceof ExtractorNoPreviousPageFoundError) {
        console.info(`Crawling ${this.site.getName()} done.`);
      } else {
        throw e;
      }
    }
  }

  private initVideos(extractor: Extractor) {
    const siteEntity = new SiteEntity();

    siteEntity.url = this.site.getUrl();
    siteEntity.name = this.site.getName();
    siteEntity.favicon = this.site.getFavicon();

    return zip(extractor.extractVideosUrl(), extractor.extractVideosThumbnailUrl()).map(payload => {
      const video = new Video();

      video.site = siteEntity;
      video.url = payload[0];
      video.thumbnailUrl = payload[1];

      return video;
    });
  }

  private handleVideo(video: Video, content: string) {
    const videoExtractor = new Extractor(this.site, content);

    video.title = videoExtractor.extractVideoTitle();
    video.tags = videoExtractor.extractVideoTags();
    video.duration = videoExtractor.extractVideoDuration();
  }
}

export { Crawler };
