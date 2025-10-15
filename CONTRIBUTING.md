# Contributing to Fund Project

## 開発フロー

### ブランチ戦略

- `main`: 本番環境用の安定版ブランチ
- `develop`: 開発用ブランチ
- `feature/*`: 新機能開発用ブランチ
- `fix/*`: バグ修正用ブランチ
- `docs/*`: ドキュメント更新用ブランチ

### コミットメッセージの規約

```
<type>: <subject>

<body>

<footer>
```

#### Type
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメントのみの変更
- `style`: フォーマット、セミコロン忘れなど（コード変更なし）
- `refactor`: リファクタリング
- `test`: テストの追加・修正
- `chore`: ビルドプロセスやツールの変更

#### 例
```
docs: 投資委員会資料フォーマットの更新

セクション3に新しい指標を追加
LP開示のマスキング規則を明確化
```

## Pull Requestの作成

1. 作業用ブランチを作成
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. 変更をコミット
   ```bash
   git add .
   git commit -m "feat: 機能の説明"
   ```

3. プッシュしてPR作成
   ```bash
   git push origin feature/your-feature-name
   ```

## レビュープロセス

1. PRテンプレートに従って内容を記載
2. 最低1名のレビュアーを指定
3. すべてのチェックリストを完了
4. レビュアーの承認後にマージ

## ドキュメント更新のガイドライン

- 明確で簡潔な日本語を使用
- 実務に即した具体例を含める
- 関連ドキュメントへのリンクを追加
- 変更履歴を更新
