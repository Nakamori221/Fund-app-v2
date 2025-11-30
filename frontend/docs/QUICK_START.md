# 🚀 Fund デモ - クイックスタートガイド

## ✅ 開発環境の準備状況

現在の状態：
- ✅ Node.js v22.16.0 インストール済み
- ✅ npm v10.9.2 インストール済み
- ✅ プロジェクト構造作成済み
- ✅ 設定ファイル作成済み

## 📦 インストール手順（エラー回避版）

### Step 1: フロントエンドディレクトリに移動

```powershell
cd frontend
```

### Step 2: 依存関係のインストール

**重要**: エラーが発生した場合は、以下の手順で対処してください。

```powershell
# 方法1: 通常のインストール（推奨）
npm install

# 方法2: エラーが出た場合の対処
# 1. node_modulesとロックファイルを削除
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item package-lock.json -ErrorAction SilentlyContinue

# 2. npmキャッシュをクリア
npm cache clean --force

# 3. 再インストール（時間がかかります）
npm install --legacy-peer-deps
```

**インストール時間**: 初回は5-10分かかる場合があります

### Step 3: 開発サーバーの起動

```powershell
npm run dev
```

**成功すると以下のように表示されます:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

ブラウザで **http://localhost:3000** を開いてください！

---

## 🎯 デモの確認方法

### 1. ログイン画面
- 任意のメールアドレスとパスワードを入力
- 「ログイン」ボタンをクリック
- **デモモード**: 実際の認証は不要です

### 2. ダッシュボード画面
以下の要素が表示されます：
- 📊 **統計カード**: 総案件数、進行中案件、観察記録数、矛盾数、承認待ち
- 📝 **最近の活動**: 最新のアクティビティログ
- 📋 **案件一覧テーブル**: 最近の案件リスト
- ⚡ **クイックアクション**: 新規案件作成、観察記録追加、矛盾検出

---

## 🔧 トラブルシューティング

### ❌ `npm install` が失敗する

**エラーメッセージ別の対処法:**

1. **ETARGET エラー（パッケージが見つからない）**
   ```powershell
   npm install --legacy-peer-deps
   ```

2. **ネットワークエラー**
   ```powershell
   # プロキシ設定を確認
   npm config get proxy
   npm config get https-proxy
   
   # 必要に応じて設定を削除
   npm config delete proxy
   npm config delete https-proxy
   ```

3. **権限エラー（Windows）**
   - PowerShellを「管理者として実行」で起動
   - または、`npm install`を実行

4. **メモリ不足エラー**
   ```powershell
   # Node.jsのメモリ制限を増やす
   $env:NODE_OPTIONS="--max-old-space-size=4096"
   npm install
   ```

### ❌ ポート3000が既に使用されている

```powershell
# 別のポートで起動（例: 3001）
npm run dev -- --port 3001
```

### ❌ TypeScriptエラーが表示される

```powershell
# 型チェックのみ実行
npm run type-check

# エラーがあっても開発サーバーは起動します
npm run dev
```

---

## 📝 次のステップ

1. ✅ **開発環境セットアップ完了**
2. ⏭️ **デザインの適用**（Gemini 3.0で生成したデザインを適用）
3. ⏭️ **バックエンドAPIとの接続**（オプション）
4. ⏭️ **追加機能の実装**

---

## 💡 便利なコマンド

```powershell
# 開発サーバー起動
npm run dev

# 型チェック
npm run type-check

# コードフォーマット
npm run format

# Lintチェック
npm run lint

# 本番ビルド
npm run build

# ビルド結果のプレビュー
npm run preview
```

---

## 📚 詳細情報

- **詳細セットアップ**: `SETUP.md` を参照
- **インストール手順**: `INSTALL.md` を参照
- **プロジェクト概要**: `README.md` を参照

---

**問題が解決しない場合**: 
1. `node_modules`フォルダを削除して再インストール
2. Node.jsとnpmのバージョンを確認（Node >= 18, npm >= 9）
3. インターネット接続を確認

