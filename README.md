# Save Liked Post in Notion

このプロジェクトは、X（旧Twitter）でいいねしたツイートを自動的にNotionのデータベースに保存するサービスです。

## 概要

IFTTTのトリガーを使用して、Xでいいねした投稿を検知し、Webhookを介してデータを受け取り、指定されたNotionデータベースに保存します。

### 保存されるデータ

- テキスト（ツイート本文）
- ユーザー名（ツイート発信者）
- ツイートへのリンク
- 作成日時
- ツイート埋め込みコード

## アーキテクチャ

- バックエンド: Python (FastAPI)
- インフラ: Google Cloud Run
- 外部サービス:
  - IFTTT (トリガー)
  - Notion API (データ保存先)

## セットアップ

### 必要条件

- Python 3.9以上
- Google Cloud アカウント
- Notion アカウントとAPI Key
- IFTTT アカウント

### ローカル開発環境のセットアップ

1. リポジトリのクローン
```bash
git clone https://github.com/yukinakai/save_liked_post_in_notion.git
cd save_liked_post_in_notion
```

2. 仮想環境の作成と有効化
```bash
python -m venv venv
source venv/bin/activate  # Unix系
# または
.\venv\Scripts\activate  # Windows
```

3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

4. 環境変数の設定
```bash
cp .env.example .env
# .envファイルを編集し、必要な環境変数を設定
```

### デプロイ

Google Cloud Runへのデプロイ手順は[GCP環境構築手順](docs/gcp-setup.md)を参照してください。

### 利用可能なコマンド

プロジェクトルートにある`Makefile`を使用して、以下のコマンドを実行できます：

```bash
# ローカル開発
make run-local    # 開発サーバーを起動（ホットリロード有効）
make test         # テストを実行
make clean        # キャッシュファイルなどをクリーンアップ

# デプロイ
make deploy       # Cloud Runへデプロイ
```

詳細な使用方法は[GCP環境構築手順](docs/gcp-setup.md)を参照してください。

## 開発ガイドライン

### テスト

- ユニットテスト: `pytest`を使用
- 統合テスト: 最小限に抑える
- E2Eテスト: 別途実施（このリポジトリには含まない）

### コミット規約

Conventional Commitsに従います：

- feat: 新機能
- fix: バグ修正
- docs: ドキュメントのみの変更
- style: コードの意味に影響を与えない変更（空白、フォーマット、セミコロンの欠落など）
- refactor: バグを修正せず、機能を追加しないコード変更
- test: テストの追加または修正
- chore: ビルドプロセスやドキュメント生成などの補助ツールやライブラリの変更

## ライセンス

MIT License
