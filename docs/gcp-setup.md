# Google Cloud Platform環境構築手順

このドキュメントでは、Save Liked Post in NotionプロジェクトのGoogle Cloud Platform（GCP）環境構築手順について説明します。

## 前提条件

- Google Cloudアカウントを持っていること
- Google Cloud CLIがインストールされていること
- プロジェクトのローカル開発環境が整っていること

## 1. GCPプロジェクトの作成と請求先設定

1. Google Cloud Consoleにアクセスし、新しいプロジェクトを作成します：

```bash
# プロジェクトの作成
gcloud projects create save-liked-post-notion --name="Save Liked Post in Notion"

# プロジェクトの設定
gcloud config set project save-liked-post-notion
```

2. 請求先アカウントの設定：

- [Google Cloud Console](https://console.cloud.google.com/billing)にアクセス
- 「請求先アカウントをリンク」をクリック
- 既存の請求先アカウントを選択するか、新しい請求先アカウントを作成
- プロジェクトと請求先アカウントをリンク

注意：GCPの一部のサービスは有料です。料金の詳細は[Google Cloud の料金](https://cloud.google.com/pricing)を参照してください。新規アカウントには無料枠があり、多くの場合、開発やテスト目的での使用であれば無料枠内で収まります。

## 2. 必要なAPIの有効化

以下のAPIを有効化します：

```bash
# Cloud Run APIの有効化
gcloud services enable run.googleapis.com

# Cloud Build APIの有効化（コンテナのビルドに必要）
gcloud services enable cloudbuild.googleapis.com
```

## 3. サービスアカウントの作成と設定

```bash
# サービスアカウントの作成
gcloud iam service-accounts create webhook-service \
    --display-name="Webhook Service Account"

# 必要な権限の付与
gcloud projects add-iam-policy-binding save-liked-post-notion \
    --member="serviceAccount:webhook-service@save-liked-post-notion.iam.gserviceaccount.com" \
    --role="roles/run.invoker"
```

## 4. ローカル開発環境からのデプロイ

1. アプリケーションのビルドとデプロイ：

```bash
# Cloud Runへのデプロイ
gcloud run deploy webhook-service \
    --source . \
    --region asia-northeast1 \
    --platform managed \
    --allow-unauthenticated \
    --service-account webhook-service@save-liked-post-notion.iam.gserviceaccount.com
```

## 5. セキュリティ設定

### 認証設定

- Cloud RunのサービスはデフォルトでIAM認証が必要です
- このプロジェクトではIFTTTからのWebhookを受け取るため、`--allow-unauthenticated`フラグを使用しています
- 追加のセキュリティ層として、Webhookエンドポイントで独自の認証トークンを実装することを推奨します

### 環境変数の設定

機密情報は環境変数として設定します：

```bash
gcloud run services update webhook-service \
    --set-env-vars="NOTION_API_KEY=your_notion_api_key" \
    --set-env-vars="WEBHOOK_SECRET=your_webhook_secret"
```

## 6. 動作確認

デプロイ後のエンドポイントURLは以下のコマンドで確認できます：

```bash
gcloud run services describe webhook-service \
    --platform managed \
    --region asia-northeast1 \
    --format='value(status.url)'
```

このURLをIFTTTのWebhookアクションで使用します。
