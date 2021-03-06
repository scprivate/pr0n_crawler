import * as Logger from '@kocal/logger';
import syncRequest from 'sync-request';
import { zip } from 'zip-array';
import { apiKey, graphqlEndpoint } from '../config';
import { Site as SiteEntity } from './entities/Site';
import { Video } from './entities/Video';
import ExtractorNoPreviousPageFoundError from './errors/ExtractorNoPreviousPageFoundError';
import { Extractor } from './Extractor';
import { Site } from './Site';

class Crawler {
  private crawledPages: number;
  private crawledVideos: number;

  constructor(private logger: Logger, private site: Site) {
    this.crawledPages = 0;
    this.crawledVideos = 0;

    /* tslint:disable max-line-length */
    this.logger.setFormat(
      (ctx, vars) =>
        `${ctx.luxon.toFormat('yyyy-LL-dd TT')} :: ${ctx.name} [P:${vars.pages}|V:${vars.videos}] :: ${ctx.levelColor(
          ctx.level
        )} :: ${ctx.message}`
    );

    this.logger.setVariables(() => ({
      pages: this.crawledPages,
      videos: this.crawledVideos,
    }));
  }

  public crawl(url: string = this.site.getEntryPoint()) {
    this.logger.info(`Fetching ${url}...`);

    const extractor = new Extractor(this.site, syncRequest('GET', url).getBody('utf8'));
    const videos: Video[] = this.initVideos(extractor);

    videos.map(async video => {
      const response = syncRequest('GET', video.url);
      this.handleVideo(video, response.getBody('utf8'));
      this.crawledVideos += 1;
    });

    this.crawledPages += 1;
    this.logger.info(`Fetching ${url}... done`);

    try {
      const previousPage = extractor.extractPreviousPage();
      this.crawl(previousPage);
    } catch (e) {
      if (e instanceof ExtractorNoPreviousPageFoundError) {
        this.logger.info(`Crawling ${this.site.getName()}: done.`);
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

    const mutation = `
      mutation CreateVideo($input: CreateVideoInput!) {
        createVideo(input: $input) {
          id title url thumbnailUrl duration
          site { id name host }
          tags { id tag slug }
        }
      }
    `;

    const variables = {
      input: {
        title: video.title,
        url: video.url,
        thumbnailUrl: video.thumbnailUrl,
        duration: video.duration,
        site: {
          name: video.site.name,
          host: video.site.url,
        },
        tags: video.tags,
      },
    };

    this.logger.info(`Sending video ${video.title} to GraphQL API...`);

    const result = syncRequest('POST', graphqlEndpoint, {
      headers: {
        'x-auth-token': apiKey,
      },
      json: {
        variables,
        query: mutation,
      },
    });

    try {
      const body = result.getBody('utf8');
      this.logger.info(`Sending video ${video.title} to GraphQL API: done`);
    } catch (e) {
      this.logger.error(`Sending video ${video.title} to GraphQL API: error`);
      console.error(e);
      process.exit(1);
    }
  }
}

export { Crawler };
