# 開発環境セットアップガイド

## 📋 前提条件

### 1. Node.js のインストール確認

```bash
node --version
# 推奨: v18.0.0 以上

npm --version
# 推奨: v9.0.0 以上
```

**Node.jsがインストールされていない場合:**
- [Node.js公式サイト](https://nodejs.org/)からLTS版をダウンロード・インストール
- または [nvm](https://github.com/nvm-sh/nvm) を使用してインストール

### 2. Git のインストール確認（オプション）

```bash
git --version
```

---

## 🚀 セットアップ手順

### Step 1: プロジェクトディレクトリに移動

```bash
cd frontend
```

### Step 2: 依存関係のインストール

```bash
npm install
```

このコマンドで以下がインストールされます：
- React 18.2
- TypeScript 5.3
- Vite 5.0
- TanStack Query
- Zustand
- Axios
- React Router
- その他の開発依存関係

**インストール時間**: 約2-5分（ネットワーク速度による）

### Step 3: 環境変数の設定（オプション）

開発環境では、デフォルト設定で動作しますが、カスタマイズする場合は：

```bash
# .env ファイルを作成（.env.exampleを参考に）
cp .env.example .env

# 必要に応じて編集
# VITE_API_BASE_URL=http://localhost:8000
```

**注意**: `.env`ファイルは`.gitignore`に含まれているため、Gitにはコミットされません。

### Step 4: 型チェックの確認

```bash
npm run type-check
```

エラーがないことを確認してください。

### Step 5: 開発サーバーの起動

```bash
npm run dev
```

ブラウザで `http://localhost:3000` を開いてください。

---

## 🛠️ よく使うコマンド

### 開発

```bash
# 開発サーバー起動（ホットリロード有効）
npm run dev

# 型チェックのみ実行
npm run type-check

# コードフォーマット
npm run format

# Lintチェック
npm run lint
```

### ビルド

```bash
# 本番用ビルド
npm run build

# ビルド結果のプレビュー
npm run preview
```

### テスト

```bash
# ユニットテスト実行
npm run test

# テストUI起動
npm run test:ui

# カバレッジレポート生成
npm run test:coverage

# E2Eテスト（Cypress）
npm run test:e2e
```

### API型定義の生成

バックエンドAPIが起動している状態で：

```bash
npm run generate:api-types
```

---

## 🔧 トラブルシューティング

### 問題1: `npm install` が失敗する

**解決策:**
```bash
# node_modulesとロックファイルを削除
rm -rf node_modules package-lock.json

# キャッシュをクリア
npm cache clean --force

# 再インストール
npm install
```

### 問題2: ポート3000が既に使用されている

**解決策:**
```bash
# 別のポートで起動（例: 3001）
npm run dev -- --port 3001
```

または、`vite.config.ts`の`server.port`を変更

### 問題3: TypeScriptエラーが表示される

**解決策:**
```bash
# 型定義を再生成
npm run type-check

# エラーの詳細を確認
npm run type-check -- --pretty
```

### 問題4: バックエンドAPIに接続できない

**確認事項:**
1. バックエンドサーバーが起動しているか確認
   ```bash
   curl http://localhost:8000/health
   ```

2. `vite.config.ts`のプロキシ設定を確認
3. CORS設定が正しいか確認（バックエンド側）

### 問題5: モジュールが見つからないエラー

**解決策:**
```bash
# 依存関係を再インストール
rm -rf node_modules
npm install
```

---

## 📦 推奨開発ツール

### VS Code拡張機能

以下の拡張機能をインストールすることを推奨します：

1. **ESLint** - コード品質チェック
2. **Prettier** - コードフォーマット
3. **TypeScript Vue Plugin (Volar)** - TypeScriptサポート
4. **React snippets** - React開発の効率化
5. **Error Lens** - エラーをインライン表示

### VS Code設定（推奨）

`.vscode/settings.json`を作成：

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true
}
```

---

## 🎯 次のステップ

1. ✅ 開発環境のセットアップ完了
2. ⏭️ デザインの適用（Gemini 3.0で生成したデザイン）
3. ⏭️ バックエンドAPIとの接続
4. ⏭️ 追加機能の実装

---

## 📚 参考リンク

- [Vite公式ドキュメント](https://vitejs.dev/)
- [React公式ドキュメント](https://react.dev/)
- [TypeScript公式ドキュメント](https://www.typescriptlang.org/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Zustand](https://github.com/pmndrs/zustand)

---

**問題が発生した場合**: プロジェクトのREADME.mdまたはこのドキュメントを確認してください。


