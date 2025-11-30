# 📦 インストール手順（簡易版）

## 必須: インストールが必要なもの

### 1. Node.js のインストール

**Windowsの場合:**
1. [Node.js公式サイト](https://nodejs.org/)にアクセス
2. LTS版（推奨版）をダウンロード
3. インストーラーを実行（デフォルト設定でOK）
4. インストール後、PowerShellまたはコマンドプロンプトを再起動

**確認コマンド:**
```powershell
node --version
# v18.0.0 以上が表示されればOK

npm --version
# v9.0.0 以上が表示されればOK
```

---

## 🚀 プロジェクトのセットアップ

### Step 1: フロントエンドディレクトリに移動

```powershell
cd frontend
```

### Step 2: 依存関係をインストール

```powershell
npm install
```

**所要時間**: 約2-5分（初回は時間がかかります）

**インストールされるもの:**
- React 18.2（UIライブラリ）
- TypeScript 5.3（型安全性）
- Vite 5.0（ビルドツール）
- TanStack Query（データフェッチング）
- Zustand（状態管理）
- Axios（HTTPクライアント）
- その他必要なパッケージ

### Step 3: 開発サーバーを起動

```powershell
npm run dev
```

**成功すると以下のように表示されます:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

ブラウザで `http://localhost:3000` を開いてください！

---

## ✅ 動作確認

### 1. ログイン画面が表示される
- 任意のメールアドレスとパスワードでログインできます（デモモード）

### 2. ダッシュボードが表示される
- 統計カード
- 最近の活動
- 案件一覧テーブル

---

## 🔧 トラブルシューティング

### ❌ `npm install` が失敗する

**解決策:**
```powershell
# node_modulesフォルダを削除
Remove-Item -Recurse -Force node_modules

# package-lock.jsonを削除（存在する場合）
Remove-Item package-lock.json -ErrorAction SilentlyContinue

# 再インストール
npm install
```

### ❌ ポート3000が既に使用されている

**解決策:**
1. 別のアプリケーションがポート3000を使用している可能性があります
2. `vite.config.ts`の`server.port`を変更するか
3. 使用しているアプリを終了してください

### ❌ `node`コマンドが見つからない

**解決策:**
1. Node.jsが正しくインストールされているか確認
2. PowerShellを再起動
3. 環境変数PATHにNode.jsが含まれているか確認

---

## 📝 次のステップ

1. ✅ インストール完了
2. ✅ 開発サーバー起動
3. ⏭️ **デザインの適用**（Gemini 3.0で生成したデザインを適用）
4. ⏭️ バックエンドAPIとの接続

---

**詳細なセットアップ情報**: `SETUP.md` を参照してください。


