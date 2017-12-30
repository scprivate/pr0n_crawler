abstract class Site {
  public abstract getUrl(): string;

  public abstract getName(): string;

  public abstract getFavicon(): string;

  public abstract getEntryPoint(): string;

  public abstract getFields(): SiteFields;
}

export { Site };
