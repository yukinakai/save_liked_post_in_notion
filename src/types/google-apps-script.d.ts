declare namespace GoogleAppsScript {
  export namespace Content {
    export interface TextOutput {
      setMimeType(mimeType: string): TextOutput;
      setContent(content: string): TextOutput;
      getContent(): string;
      getResponseCode(): number;
      setResponseCode(code: number): TextOutput;
    }
  }

  export namespace ContentService {
    export interface ContentService {
      MimeType: {
        JSON: string;
      };
      createTextOutput(): Content.TextOutput;
    }
  }
}

declare const ContentService: GoogleAppsScript.ContentService.ContentService;
