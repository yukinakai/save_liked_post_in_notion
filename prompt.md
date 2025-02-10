<!--
Copyright 2025 Yuki Nakai

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->
あなたはシニアエンジニアです。
以下の要件のプロダクトを実現するために、あなたの部下のジュニアエンジニアに実装を指示してプロダクトをデリバリーすることがあなたのミッションです。
そのために以下の要件をなるべく小さなissueに分割し、githubのissueとして起案します。
Titleとdescriptionを考えてください。

## 要件
- GASを使って、notionの指定のdatabaseにページを追加するスクリプトを開発します。
- このスクリプトは、webhookになっており、外部からtext,userName,linkToTweet,createdAt,tweetEmbedCodeを受け取ります。
- 受け取った内容を元にnotionのdatabaseにページを追加します。
- notionのプロパティのIDプロパティにuserName、Textプロパティにtext、URLプロパティにlinkToTweetをTweeted_atプロパティにcreatedAtを追加します。
- notionのページボディにtweetEmbedCodeを追加します。
- フレームワークとして、asideを利用し、typescriptで実装します。
