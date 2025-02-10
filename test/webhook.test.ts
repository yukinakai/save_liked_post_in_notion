import { doPost } from '../src';

// Google Apps Scriptのモック
const mockTextOutput = {
  setMimeType: jest.fn().mockReturnThis(),
  setContent: jest.fn().mockReturnThis(),
  getContent: jest.fn(),
  getResponseCode: jest.fn(),
};

const mockContentService = {
  MimeType: {
    JSON: 'application/json',
  },
  createTextOutput: jest.fn().mockReturnValue(mockTextOutput),
};

// @ts-ignore
global.ContentService = mockContentService;

describe('webhook endpoint', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockTextOutput.getContent.mockImplementation(function(this: any) {
      return this.content;
    });
    mockTextOutput.setContent.mockImplementation(function(this: any, content: string) {
      this.content = content;
      return this;
    });
    mockTextOutput.getResponseCode.mockImplementation(function(this: any) {
      return this.responseCode;
    });
    // @ts-ignore
    mockTextOutput.setResponseCode = function(this: any, code: number) {
      this.responseCode = code;
      return this;
    };
  });

  it('should return 400 when required parameters are missing', () => {
    const e = {
      postData: {
        contents: JSON.stringify({
          // missing required parameters
        }),
      },
    };

    const result = doPost(e as any);
    const response = JSON.parse(result.getContent());

    expect(result.getResponseCode()).toBe(400);
    expect(response.error).toBeDefined();
  });

  it('should return 200 with valid parameters', () => {
    const e = {
      postData: {
        contents: JSON.stringify({
          text: 'Test tweet text',
          userName: 'testUser',
          linkToTweet: 'https://twitter.com/test/status/123',
          createdAt: '2025-02-10T09:20:29Z',
          tweetEmbedCode: '<blockquote>Test embed code</blockquote>',
        }),
      },
    };

    const result = doPost(e as any);
    const response = JSON.parse(result.getContent());

    expect(result.getResponseCode()).toBe(200);
    expect(response.success).toBe(true);
  });

  it('should validate createdAt format', () => {
    const e = {
      postData: {
        contents: JSON.stringify({
          text: 'Test tweet text',
          userName: 'testUser',
          linkToTweet: 'https://twitter.com/test/status/123',
          createdAt: 'invalid-date',
          tweetEmbedCode: '<blockquote>Test embed code</blockquote>',
        }),
      },
    };

    const result = doPost(e as any);
    const response = JSON.parse(result.getContent());

    expect(result.getResponseCode()).toBe(400);
    expect(response.error).toContain('createdAt');
  });
});
