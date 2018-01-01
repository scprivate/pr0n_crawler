import { Site } from '../Site';
import ExtractorError from './ExtractorError';

class ExtractorNoPreviousPageFoundError extends ExtractorError {
  constructor(site: Site) {
    super(site, 'No previous page found.');
  }
}

export default ExtractorNoPreviousPageFoundError;
