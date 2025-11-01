---
title: Phase 1 データ投入候補リスト（P1-A）
作成日: 2025-10-28
作成者: Codex（GPT-5）
---

## 1. 既存資料からの抽出候補
| 優先度 | ソース | 想定フィールド例 | 備考（タグ/取得先） |
| --- | --- | --- | --- |
| 高 | ファンド内部メモ（機密） | `deal.investment_amount`, `deal.key_terms_summary` | CONF、Phase 2以降で本格投入。現時点はダミー/サンプルで代替 |
| 高 | 公式プレス／登記（公開） | `business.problem_summary`, `product.overview` | PUB。Phase 1 で具体資料を収集しCSVに追記 |
| 中 | 外部推定データ（Similarweb 等） | `market.size_tam`, `market.size_sam`, `market.size_som` | EXT。契約/API状況に応じて後追い（Phase 1.5〜） |
| 中 | 既存分析（Step 1〜4 ドキュメント） | `risk.top_list`, `value_creation.plan_summary` | ANL。ダミー値→実値へ更新予定 |
| 低 | インタビュー起点の情報 | `team.gap_and_plan`, `int.questions` | INT。Phase 3で実施 |

## 2. CSV草稿ラインナップ（例）
| シート/ファイル | コメント | 今後の作業 |
| --- | --- | --- |
| `observations_fund_phase1.csv` | Fund案件の初期観測値（PUB/CONF/ANLタグ混在） | 10/29以降で初版を作成し、テンプレ案に沿って項目入力 |
| `conf_placeholders.csv` | CONF想定のカラムサンプル（Term Sheet等） | Phase 2 で本格運用。現時点では空テンプレを整備 |
| `int_questionnaire.csv` | INT入力フォーマット（役職別質問＋回答欄） | Phase 3 に備え Step4-1のテンプレを整備 |

## 3. アクションアイテム（P1-A）
1. 公開情報（プレスリリース、登記情報）から `business.*` フィールドに該当する内容を抜粋し、CSV草稿に追加  
2. 既存分析資料（Step 1〜4）から数値/テキストを`ANL`としてマッピングし、暫定的に観測値を埋める  
3. 欠損セルは `value_status: pending`（CSVでは空欄＋`notes`に pending 記載）で明示し、ギャップ検出の対象にする
