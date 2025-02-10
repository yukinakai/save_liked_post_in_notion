# Save Liked Post in Notion

TwitterやInstagramなどのSNSでいいねした投稿をNotionに自動保存するGoogle Apps Scriptプロジェクトです。

## 開発環境

- Node.js >= 12
- TypeScript
- Google Apps Script
- Jest（テストフレームワーク）

## プロジェクト構成

```
.
├── src/                    # ソースコード
│   ├── index.ts           # エントリーポイント
│   └── modules/           # 機能モジュール
├── test/                  # テストコード
│   └── modules/           # モジュールのテスト
├── dist/                  # ビルド成果物
├── appsscript.json        # GASプロジェクト設定
├── tsconfig.json          # TypeScript設定
├── rollup.config.mjs      # Rollup設定
├── jest.config.json       # Jest設定
└── package.json           # プロジェクト依存関係
```

## セットアップ

1. 依存パッケージのインストール
```bash
npm install
```

2. ビルド
```bash
npm run build
```

3. デプロイ（開発環境）
```bash
npm run deploy
```

4. デプロイ（本番環境）
```bash
npm run deploy:prod
```

## 開発フロー

1. 機能の実装
   - `src/modules/`に新しい機能モジュールを作成
   - `test/modules/`に対応するテストを作成

2. テストの実行
```bash
npm run test
```

3. リントチェック
```bash
npm run lint
```

## ライセンス

Apache-2.0
