import { Site } from '../Site';

class ExtractorError extends Error {
  constructor(site: Site, message: string) {
    super(`[Extractor] ${site.getName()}: ${message}`);
  }
}

export default ExtractorError;
