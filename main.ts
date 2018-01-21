import fetch from 'node-fetch';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { ApolloClient } from 'apollo-client';
import { HttpLink } from 'apollo-link-http';

import { graphqlEndpoint, jwtToken } from './config';
import { Crawler } from './src/Crawler';
import { YouJizzSite } from './src/sites/youjizz';

const client = new ApolloClient({
  link: new HttpLink({
    fetch,
    uri: graphqlEndpoint,
    headers: {
      authorization: `Bearer ${jwtToken}`,
    },
  }),
  cache: new InMemoryCache(),
});

const site = new YouJizzSite();

const crawler = new Crawler(client, site);
crawler.crawl();
