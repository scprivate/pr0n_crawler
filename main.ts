import * as Logger from '@kocal/logger';
import { Crawler } from './src/Crawler';
import { YouJizzSite } from './src/sites/youjizz';

const site = new YouJizzSite();

const crawler = new Crawler(Logger.getLogger('YouJizz'), site);
crawler.crawl();
