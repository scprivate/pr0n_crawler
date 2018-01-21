import { Site } from '../Site';
import ExtractorError from './ExtractorError';

class ExtractorNoPreviousPageFoundError extends ExtractorError {
  constructor(site: Site) {
    super(site, 'No previous page found.');
    Object.setPrototypeOf(this, ExtractorNoPreviousPageFoundError.prototype);
  }
}

export default ExtractorNoPreviousPageFoundError;
