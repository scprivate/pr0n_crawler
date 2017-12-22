const isProduction = process.env.NODE_ENV === 'production';

export const jwtToken = isProduction
  ? 'aaaa'
  : 'qsdqsd';

export const graphqlEndpoint = isProduction
  ? 'ddds'
  : 'https://example.com/graphql/';
