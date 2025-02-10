/**
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
/* eslint-disable @typescript-eslint/no-unused-vars */

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

function createResponse(code: number, body: WebhookResponse): GoogleAppsScript.Content.TextOutput {
  const response = ContentService.createTextOutput();
  response.setMimeType(ContentService.MimeType.JSON);
  response.setContent(JSON.stringify(body));
  // @ts-ignore
  response.setResponseCode(code);
  return response;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function doPost(e: any): GoogleAppsScript.Content.TextOutput {
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
}
