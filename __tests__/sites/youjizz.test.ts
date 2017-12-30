import { readFile } from 'async-file';
import { Extractor } from '../../src/Extractor';
import { YouJizzSite } from '../../src/sites/youjizz';

const fixtures = `${__dirname}/fixtures`;

describe('Site - YouJizz', () => {
  const youjizz = new YouJizzSite();

  describe('entry point', () => {
    let extractor;

    beforeEach(async (done) => {
      const content = await readFile(`${fixtures}/youjizz-entry-point.html`, 'utf8');
      extractor = new Extractor(youjizz, content);

      done();
    });

    it('it should extracts previousPage', () => {
      expect(extractor.extractPreviousPage()).toMatchSnapshot();
    });

    it('it should extracts videosUrl', () => {
      expect(extractor.extractVideosUrl()).toMatchSnapshot();
    });

    it('it should extracts videosThumbnailUrl', () => {
      expect(extractor.extractVideosThumbnailUrl()).toMatchSnapshot();
    });
  });
});
