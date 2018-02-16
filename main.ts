import { Crawler } from './src/Crawler';
import { YouJizzSite } from './src/sites/youjizz';

const site = new YouJizzSite();

const crawler = new Crawler(site);
crawler.crawl();
