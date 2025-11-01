---
title: Fund MVP 既存資料インベントリ（Phase 1 着手準備）
作成日: 2025-10-28
作成者: Codex（GPT-5）
---

## 1. 資料インベントリ（抜粋）
| ファイル | 概要 | 想定ソース区分 / 用途 |
| --- | --- | --- |
| `MVPを設計する前の仕様の再確認.md` | 現状仕様・MVP要件・議論論点の整理 | ANL（要件定義）、Phase全体の参照 |
| `MVP準備計画.md` | フェーズ構成・マイルストーン・リスク整理（Phase 0完了追記済み） | ANL、プロジェクト管理 |
| `MVPスキーマ草案.md` | 観測テーブル／ギャップテーブル／レポートテンプレのスキーマ草案とフィールド辞書ドラフト | ANL、Phase 1 実装の参照 |
| `Step 1：指標定義辞書.md` | ARR/ARPU/Churn等の定義・式・ルール | ANL → `field_dictionary_v0_1.json` の根拠 |
| `Step 2：セクター別マルチプルの“構造と収集ルール.md` | マルチプル構造・収集ルール | ANL、Phase 1.5～2 以降で利用 |
| `Step 3：LP開示のマスキング規則（実務版 v0.1）.md` | マスキングポリシー方針 | ANL → `lp_masking_policy_v0_1.json` 根拠 |
| `Step 4（ダミー案件で一巡テスト）.md` | NimbusFlowダミーデータによるワークフロー検証 | ANL、Phase 1 テスト計画 |
| `Step4-1テストのダミー素材一覧.md` | ダミーデータ素材とテンプレ | ANL、Phase 1 データ投入時の参考 |
| `automation_roadmap.md`, `development_plan.md` など | 上位ロードマップ、開発方針 | ANL、Phase全体の参照 |
| `scripts/` 配下（`lp_masking.py`, `render_report_markdown.py`, `gap_sync.py` など） | マスキング・レポート生成・ギャップ検出スクリプト | ANL（実装資産）、Phase 1 テスト／運用で活用 |
| `tests/fixtures/observations_lp_sample.json` | ダミー観測値 | ANL → Phase 1 データ投入の雛形 |
| `tests/fixtures/expected_lp_output.json` | マスキング期待値 | ANL → 回帰テスト |
| `tests/artifacts/*.md/json` | 最新プレビュー／ギャップ検出結果 | ANL → Phase 1 検証ログ |

## 2. タグ付けポリシー草案（Phase 1 用）
| タグ | 定義 | 具体例 | 補足 |
| --- | --- | --- | --- |
| **PUB** | 公開情報：プレスリリース、公式サイト、採用ページ等 | `automation_roadmap.md` 内の公知情報、今後収集する企業サイト資料 | Phase 1 では別ファイル収集後に適用 |
| **EXT** | 推定データ：Similarweb、Crunchbase等の外部API | Phase 1 では未取得。Step2 に基づき追加予定 | API連携設計時に反映 |
| **CONF** | 社内・機密文書：Term Sheet、Cap Table等 | まだ未投入。Phase 2でGDrive等から取得しタグ付け | マスキング対象 |
| **INT** | インタビュー記録 | Phase 3から。質問票テンプレ作成済み（Step4-1参照） | 録音/要約テキスト想定 |
| **ANL** | 分析・設計ドキュメント | `MVP準備計画.md`, `MVPスキーマ草案.md`, `Step` シリーズ, `scripts/` | 現在の主要ドキュメントはANLタグに分類 |

## 3. Phase 1 作業メモ
- **既存資料の棚卸し**: 上記の通りANLタグ中心。PUB/EXT/CONF/INTに分類される一次ソースはこれから収集。
- **次アクション**: 
  1. `P1-2` として外部資料（公開情報/登記等）の収集リストを起票し、タグ振り計画を具体化する。  
  2. `P1-3` のデータ投入テンプレ案を作成（CSV/フォーム）。  
  3. ダミーデータを用いた `render_report_markdown.py` / `gap_sync.py` の回帰テスト手順を整備し、テンプレ化する。
