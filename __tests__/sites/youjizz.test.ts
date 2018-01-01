import { readFile } from 'async-file';
import { Extractor } from '../../src/Extractor';
import { YouJizzSite } from '../../src/sites/youjizz';

const fixtures = `${__dirname}/fixtures`;

describe('Site - YouJizz', () => {
  const youjizz = new YouJizzSite();

  describe('entry point', () => {
    let extractor;

    beforeAll(async (done) => {
      const content = await readFile(`${fixtures}/youjizz-entry-point.html`, 'utf8');
      extractor = new Extractor(youjizz, content);

      done();
    });

    it('should extracts previousPage', () => {
      expect(extractor.extractPreviousPage()).toMatchSnapshot();
    });

    it('should extracts videosUrl', () => {
      expect(extractor.extractVideosUrl()).toMatchSnapshot();
    });

    it('should extracts videosThumbnailUrl', () => {
      expect(extractor.extractVideosThumbnailUrl()).toMatchSnapshot();
    });
  });

  describe('video', () => {
    let extractor;

    beforeAll(async (done) => {
      const content = await readFile(`${fixtures}/youjizz-video.html`, 'utf8');
      extractor = new Extractor(youjizz, content);

      done();
    });

    it('should extracts title', () => {
      expect(extractor.extractVideoTitle()).toMatchSnapshot();
    });

    it('should extracts duration', () => {
      expect(extractor.extractVideoDuration()).toMatchSnapshot();
    });

    it('should extracts tags', () => {
      expect(extractor.extractVideoTags()).toMatchSnapshot();
    });
  });
});
