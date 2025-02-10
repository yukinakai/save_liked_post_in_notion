export {};

interface PostEvent {
  postData: {
    contents: string;
  };
}

interface WebhookRequest {
  text: string;
  userName: string;
  linkToTweet: string;
  createdAt: string;
  tweetEmbedCode: string;
}

interface WebhookResponse {
  success?: boolean;
  error?: string;
}

interface MockTextOutput {
  setMimeType: jest.Mock;
  setContent: jest.Mock;
  getContent: jest.Mock;
  getResponseCode: jest.Mock;
  setResponseCode: jest.Mock;
  content?: string;
  responseCode?: number;
}

// Google Apps Scriptのモック
const mockTextOutput: MockTextOutput = {
  setMimeType: jest.fn().mockReturnThis(),
  setContent: jest.fn().mockReturnThis(),
  getContent: jest.fn(),
  getResponseCode: jest.fn(),
  setResponseCode: jest.fn().mockReturnThis(),
};

const mockContentService = {
  MimeType: {
    JSON: 'application/json',
  },
  createTextOutput: jest.fn().mockReturnValue(mockTextOutput),
};

// @ts-expect-error ContentService is mocked
global.ContentService = mockContentService;

// テスト用のグローバル関数を定義
function validateRequest(request: WebhookRequest): string | null {
  if (!request.text) return 'text is required';
  if (!request.userName) return 'userName is required';
  if (!request.linkToTweet) return 'linkToTweet is required';
  if (!request.createdAt) return 'createdAt is required';
  if (!request.tweetEmbedCode) return 'tweetEmbedCode is required';

  // createdAtの日付フォーマットを検証
  const date = new Date(request.createdAt);
  if (isNaN(date.getTime())) return 'createdAt must be a valid date';

  return null;
}

function createResponse(
  code: number,
  body: WebhookResponse
): GoogleAppsScript.Content.TextOutput {
  const response = ContentService.createTextOutput();
  response.setMimeType(ContentService.MimeType.JSON);
  response.setContent(JSON.stringify(body));
  response.setResponseCode(code);
  return response;
}

// グローバル関数として定義
global.doPost = function (e: PostEvent): GoogleAppsScript.Content.TextOutput {
  console.log('Received webhook request:', e.postData.contents);

  try {
    const request: WebhookRequest = JSON.parse(e.postData.contents);
    const validationError = validateRequest(request);

    if (validationError) {
      return createResponse(400, { error: validationError });
    }

    // TODO: ここでNotionへの保存処理を実装

    return createResponse(200, { success: true });
  } catch (error) {
    console.error('Error processing webhook request:', error);
    return createResponse(400, { error: 'Invalid request format' });
  }
};

describe('webhook endpoint', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockTextOutput.getContent.mockImplementation(function (
      this: MockTextOutput
    ) {
      return this.content;
    });
    mockTextOutput.setContent.mockImplementation(function (
      this: MockTextOutput,
      content: string
    ) {
      this.content = content;
      return this;
    });
    mockTextOutput.getResponseCode.mockImplementation(function (
      this: MockTextOutput
    ) {
      return this.responseCode;
    });
    mockTextOutput.setResponseCode.mockImplementation(function (
      this: MockTextOutput,
      code: number
    ) {
      this.responseCode = code;
      return this;
    });
  });

  it('should return 400 when required parameters are missing', () => {
    const e: PostEvent = {
      postData: {
        contents: JSON.stringify({
          // missing required parameters
        }),
      },
    };

    const result = doPost(e);
    const response = JSON.parse(result.getContent());

    expect(result.getResponseCode()).toBe(400);
    expect(response.error).toBeDefined();
  });

  it('should return 200 with valid parameters', () => {
    const e: PostEvent = {
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

    const result = doPost(e);
    const response = JSON.parse(result.getContent());

    expect(result.getResponseCode()).toBe(200);
    expect(response.success).toBe(true);
  });

  it('should validate createdAt format', () => {
    const e: PostEvent = {
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

    const result = doPost(e);
    const response = JSON.parse(result.getContent());

    expect(result.getResponseCode()).toBe(400);
    expect(response.error).toContain('createdAt');
  });
});
