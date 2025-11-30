# Fund IC Automation - フロントエンド

Fund IC Automation Systemのフロントエンドアプリケーション（React + TypeScript + Vite）

## 🚀 クイックスタート

### 1. 依存関係のインストール

```powershell
cd frontend
npm install
```

**エラーが出た場合:**
```powershell
npm install --legacy-peer-deps
```

### 2. 開発サーバーの起動

```powershell
npm run dev
```

ブラウザで `http://localhost:3000` を開いてください。

### 3. デモの確認

- **ログイン**: 任意のメールアドレスとパスワードでログイン可能（デモモード）
- **ダッシュボード**: 統計カード、最近の活動、案件一覧が表示されます

---

## 📁 プロジェクト構造

```
frontend/
├── src/
│   ├── components/      # 再利用可能なコンポーネント
│   │   ├── StatCard.tsx
│   ├── RecentActivities.tsx
│   │   └── CasesTable.tsx
│   ├── pages/          # ページコンポーネント
│   │   ├── Dashboard.tsx
│   │   └── Login.tsx
│   ├── services/       # API呼び出しとビジネスロジック
│   │   ├── api.ts
│   │   └── dashboardService.ts
│   ├── stores/         # Zustandストア（状態管理）
│   │   └── authStore.ts
│   ├── types/          # TypeScript型定義
│   │   └── index.ts
│   ├── App.tsx         # メインアプリケーションコンポーネント
│   ├── main.tsx        # エントリーポイント
│   └── index.css      # グローバルスタイル
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

## 🛠️ 利用可能なコマンド

### 開発

```powershell
npm run dev          # 開発サーバー起動（ホットリロード）
npm run type-check   # TypeScript型チェック
npm run lint         # ESLintチェック
npm run format       # Prettierでコードフォーマット
```

### ビルド

```powershell
npm run build        # 本番用ビルド
npm run preview      # ビルド結果のプレビュー
```

### テスト

```powershell
npm run test         # ユニットテスト実行
npm run test:ui      # テストUI起動
npm run test:coverage # カバレッジレポート生成
```

---

## 🔧 設定ファイル

- **`vite.config.ts`**: Vite設定（ビルド、開発サーバー、プロキシ設定）
- **`tsconfig.json`**: TypeScript設定
- **`.eslintrc.cjs`**: ESLint設定
- **`.prettierrc.json`**: Prettier設定
- **`.npmrc`**: npm設定（エラー回避）

---

## 📝 環境変数

開発環境ではデフォルト設定で動作します。カスタマイズする場合は：

```powershell
# .env ファイルを作成
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1
```

---

## 🎨 デザイン適用について

現在は基本的なスタイルで実装されています。Gemini 3.0で生成したデザインを適用する場合は：

1. デザインのCSS/スタイルを `src/index.css` に追加
2. 各コンポーネントの `style` プロパティをCSSクラスに置き換え
3. 必要に応じてTailwind CSSなどのCSSフレームワークを追加

---

## 🔗 バックエンドAPIとの接続

現在はモックデータを使用しています。実際のAPIに接続するには：

1. `src/services/dashboardService.ts` のコメントアウト部分を有効化
2. バックエンドサーバーが `http://localhost:8000` で起動していることを確認
3. CORS設定が正しいことを確認

---

## 📚 ドキュメント

- **`QUICK_START.md`**: クイックスタートガイド（エラー回避版）
- **`SETUP.md`**: 詳細なセットアップガイド
- **`INSTALL.md`**: インストール手順

---

## ⚠️ トラブルシューティング

### npm install が失敗する

```powershell
# node_modulesを削除して再インストール
Remove-Item -Recurse -Force node_modules
npm install --legacy-peer-deps
```

### ポート3000が使用中

```powershell
# 別のポートで起動
npm run dev -- --port 3001
```

### TypeScriptエラー

```powershell
# 型チェックを実行してエラーを確認
npm run type-check
```

---

## 🎯 次のステップ

1. ✅ 開発環境セットアップ完了
2. ⏭️ **デザインの適用**（Gemini 3.0で生成したデザイン）
3. ⏭️ バックエンドAPIとの接続
4. ⏭️ 追加機能の実装

---

**作成日**: 2025-11-30  
**バージョン**: 1.0.0
