import { DOMParser } from 'xmldom';
import * as xpath from 'xpath';
import ExtractorError from './errors/ExtractorError';
import ExtractorNoPreviousPageFoundError from './errors/ExtractorNoPreviousPageFoundError';
import { Site } from './Site';

class Extractor {
  private doc: Node;

  constructor(private site: Site, private content: string) {
    this.doc = new DOMParser({
      errorHandler: () => null,
    }).parseFromString(content);
  }

  public extractPreviousPage(): string {
    const { selector, normalizer } = this.site.getFields().previousPage;
    const node = xpath.select(selector, this.doc, true);

    if (node === undefined) {
      throw new ExtractorNoPreviousPageFoundError(this.site);
    }

    const previousPage = (node as Node).nodeValue;

    return typeof normalizer === 'function' ? normalizer(previousPage) : previousPage;
  }

  public extractVideosUrl(): string[] {
    const { selector, normalizer } = this.site.getFields().videosUrl;
    const nodes = xpath.select(selector, this.doc);

    if (nodes.length === 0) {
      throw new ExtractorError(this.site, 'No videos found.');
    }

    const videosUrl = nodes.map(node => (node as Node).nodeValue);

    return typeof normalizer === 'function' ? normalizer(videosUrl) : videosUrl;
  }

  public extractVideosThumbnailUrl(): string[] {
    const { selector, normalizer } = this.site.getFields().videosThumbnailUrl;
    const nodes = xpath.select(selector, this.doc);

    if (nodes.length === 0) {
      throw new ExtractorError(this.site, 'No thumbnails found.');
    }

    const videosUrl = nodes.map(node => (node as Node).nodeValue);

    return typeof normalizer === 'function' ? normalizer(videosUrl) : videosUrl;
  }

  public extractVideoTitle(): string {
    const { selector, normalizer } = this.site.getFields().video.title;
    const node = xpath.select(selector, this.doc, true);

    if (node === undefined) {
      throw new ExtractorError(this.site, 'No title found for video.');
    }

    const title = (node as Node).nodeValue;

    return typeof normalizer === 'function' ? normalizer(title) : title;
  }

  public extractVideoDuration(): number | string {
    const { selector, normalizer } = this.site.getFields().video.duration;
    const node = xpath.select(selector, this.doc, true);

    if (node === undefined) {
      throw new ExtractorError(this.site, 'No duration found for video.');
    }

    const duration = (node as Node).nodeValue.trim();

    return typeof normalizer === 'function' ? normalizer(duration) : duration;
  }

  public extractVideoTags(): string[] {
    const { selector, normalizer } = this.site.getFields().video.tags;
    const nodes = xpath.select(selector, this.doc);

    if (nodes.length === 0) {
      throw new ExtractorError(this.site, 'No tags found for video.');
    }

    const tags = nodes.map(node => (node as Node).nodeValue);

    return typeof normalizer === 'function' ? normalizer(tags) : tags;
  }
}

export { Extractor };
