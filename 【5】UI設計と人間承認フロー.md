実装の成功には、使いやすいUIと効率的な承認フローが不可欠です。

# UI設計・人間承認フロー

## 1. 画面設計の全体構成

### 1-1. 画面一覧

```
├─ ダッシュボード（ホーム）
│  ├─ 案件一覧
│  ├─ タスク一覧
│  └─ アクティビティフィード
│
├─ 案件詳細
│  ├─ 概要タブ
│  ├─ 情報収集タブ
│  │  ├─ PUB（公開情報）
│  │  ├─ EXT（外部データ）
│  │  ├─ INT（インタビュー）
│  │  └─ CONF（機密資料）
│  ├─ 分析タブ
│  │  ├─ ユニットエコノミクス
│  │  ├─ 市場規模
│  │  ├─ 競合分析
│  │  └─ バリュエーション
│  ├─ タスク・質問票タブ
│  ├─ 矛盾・要確認タブ
│  └─ レポートタブ
│
├─ レポート生成
│  ├─ プレビュー
│  ├─ 編集
│  └─ エクスポート
│
└─ 設定
   ├─ テンプレート管理
   ├─ ユーザー管理
   └─ 外部連携設定
```

### 1-2. ナビゲーション設計

```
┌──────────────────────────────────────────────────────┐
│  [Logo] Fund Automation                [通知] [User]│
├──────────────────────────────────────────────────────┤
│                                                      │
│  ダッシュボード │ 案件一覧 │ タスク │ 設定         │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 2. 主要画面の詳細設計

### 2-1. ダッシュボード

```
┌────────────────────────────────────────────────────────┐
│  ダッシュボード                          2025/10/01    │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ 進行中の案件 │  │ 承認待ち    │  │ 今週のIC    │  │
│  │     8       │  │     3       │  │     2       │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
│                                                        │
│  ┌────────────────────────────────────────────────┐  │
│  │ 要対応タスク                          [すべて]│  │
│  ├────────────────────────────────────────────────┤  │
│  │ 🔴 [Critical] Acme社のTerm Sheet承認          │  │
│  │    期限: 今日                      [確認する] │  │
│  ├────────────────────────────────────────────────┤  │
│  │ 🟡 [High] Beta社 CFOへのインタビュー質問票    │  │
│  │    期限: 10/03                     [開く]     │  │
│  ├────────────────────────────────────────────────┤  │
│  │ 🟢 [Medium] Gamma社の競合情報矛盾の解決      │  │
│  │    期限: 10/05                     [確認]     │  │
│  └────────────────────────────────────────────────┘  │
│                                                        │
│  ┌────────────────────────────────────────────────┐  │
│  │ 最近のアクティビティ                          │  │
│  ├────────────────────────────────────────────────┤  │
│  │ 2分前                                          │  │
│  │ システムがAcme社のPUB収集を完了しました       │  │
│  ├────────────────────────────────────────────────┤  │
│  │ 15分前                                         │  │
│  │ 田中さんがBeta社のレポートドラフトを生成      │  │
│  ├────────────────────────────────────────────────┤  │
│  │ 1時間前                                        │  │
│  │ システムがGamma社のARRに矛盾を検出しました    │  │
│  └────────────────────────────────────────────────┘  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 2-2. 案件詳細 - 情報収集タブ

```
┌────────────────────────────────────────────────────────┐
│  Acme株式会社                                          │
│  [概要] [情報収集] [分析] [タスク] [レポート]         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  情報収集の進捗                           [更新]      │
│  ■■■■■■■□□□ 65%                                  │
│                                                        │
│  ┌─ PUB（公開情報） ────────────────────────────┐    │
│  │ ステータス: ✓ 完了 (10/01 10:30)              │    │
│  │                                                │    │
│  │ 収集項目: 15/15 完了                           │    │
│  │                                                │    │
│  │ ┌────────────────────────────────────────┐    │    │
│  │ │ 項目             値              出典   │    │    │
│  │ ├────────────────────────────────────────┤    │    │
│  │ │ 会社名         Acme株式会社      [URL] │    │    │
│  │ │ 設立           2018-04-01        [URL] │    │    │
│  │ │ 従業員数       45人              [URL] │    │    │
│  │ │ 所在地         東京都渋谷区      [URL] │    │    │
│  │ │ ...                                     │    │    │
│  │ └────────────────────────────────────────┘    │    │
│  │                                   [詳細を見る]│    │
│  └────────────────────────────────────────────────┘    │
│                                                        │
│  ┌─ EXT（外部データ） ───────────────────────────┐    │
│  │ ステータス: ⟳ 処理中 (70%)                    │    │
│  │                                                │    │
│  │ 収集項目: 7/10 完了                            │    │
│  │                                                │    │
│  │ ✓ Crunchbase - 資金調達履歴                   │    │
│  │ ✓ Similarweb - Webトラフィック               │    │
│  │ ⚠️ LinkedIn - 組織規模（推定値）               │    │
│  │   注意: 推定値のため信頼度 60%                │    │
│  │ ⟳ data.ai - アプリDL数（取得中...）          │    │
│  │                                   [詳細を見る]│    │
│  └────────────────────────────────────────────────┘    │
│                                                        │
│  ┌─ CONF（機密資料） ────────────────────────────┐    │
│  │ ステータス: ⚠️ 承認待ち                        │    │
│  │                                                │    │
│  │ アップロード済み文書: 2件                     │    │
│  │                                                │    │
│  │ ┌────────────────────────────────────────┐    │    │
│  │ │ 📄 Term_Sheet_v3.pdf                   │    │    │
│  │ │    アップロード: 10/01 09:00             │    │    │
│  │ │    抽出済み（承認待ち）   [レビュー ▶] │    │    │
│  │ ├────────────────────────────────────────┤    │    │
│  │ │ 📊 Cap_Table_2025Q3.xlsx               │    │    │
│  │ │    アップロード: 10/01 09:15             │    │    │
│  │ │    処理中...                            │    │    │
│  │ └────────────────────────────────────────┘    │    │
│  │                                                │    │
│  │ [+ 文書をアップロード]                        │    │
│  └────────────────────────────────────────────────┘    │
│                                                        │
│  ┌─ INT（インタビュー） ─────────────────────────┐    │
│  │ ステータス: 未開始                            │    │
│  │                                                │    │
│  │ 質問票: 自動生成済み（15問）                  │    │
│  │                                                │    │
│  │ [質問票を確認] [面談を記録]                   │    │
│  └────────────────────────────────────────────────┘    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 2-3. CONF承認画面（モーダル）

```
┌────────────────────────────────────────────────────────┐
│  Term Sheetからの抽出結果を確認                        │
│                                            [×閉じる]   │
├────────────────────────────────────────────────────────┤
│                                                        │
│  📄 Term_Sheet_v3.pdf                                 │
│  アップロード: 2025/10/01 09:00                       │
│  処理完了: 2025/10/01 09:05                           │
│                                                        │
│  ┌────────────────────────────────────────────────┐  │
│  │ 抽出された投資条件              信頼度: 95%   │  │
│  ├────────────────────────────────────────────────┤  │
│  │ プレマネー評価額                               │  │
│  │ ¥5,000,000,000                                 │  │
│  │ 出典: p.2 "評価額50億円（プレマネー）"        │  │
│  │ [✓ 正しい] [✗ 修正]                           │  │
│  ├────────────────────────────────────────────────┤  │
│  │ 投資額                                         │  │
│  │ ¥1,000,000,000                                 │  │
│  │ 出典: p.2 "投資額10億円"                      │  │
│  │ [✓ 正しい] [✗ 修正]                           │  │
│  ├────────────────────────────────────────────────┤  │
│  │ ポストマネー評価額                             │  │
│  │ ¥6,000,000,000                                 │  │
│  │ 出典: 計算値（プレ＋投資額）                  │  │
│  │ [✓ 正しい] [✗ 修正]                           │  │
│  ├────────────────────────────────────────────────┤  │
│  │ 取得持分                                       │  │
│  │ 16.67%                                         │  │
│  │ 出典: 計算値（投資額/ポスト）                 │  │
│  │ [✓ 正しい] [✗ 修正]                           │  │
│  ├────────────────────────────────────────────────┤  │
│  │ 清算優先                                       │  │
│  │ 1x 非参加型                                    │  │
│  │ 出典: p.5 "1倍の清算優先権（非参加型）"       │  │
│  │ [✓ 正しい] [✗ 修正]                           │  │
│  └────────────────────────────────────────────────┘  │
│                                                        │
│  ⚠️ 要確認事項                                         │
│  - 希薄化防止条項の記述が不明確です                   │
│    → "Full Ratchet" との記載がありますが、            │
│       トリガー条件の記述が見つかりません              │
│                                                        │
│  整合性チェック: ✓ 通過                               │
│  - プレ＋投資額＝ポスト ✓                             │
│  - 持分計算 ✓                                         │
│                                                        │
│  [📎 元ファイルを見る]                                │
│                                                        │
│  ┌────────────────────────────────────────────────┐  │
│  │          [承認して反映]  [修正]  [却下]       │  │
│  └────────────────────────────────────────────────┘  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 2-4. 矛盾検出画面

```
┌────────────────────────────────────────────────────────┐
│  Acme株式会社 - 矛盾・要確認事項                       │
├────────────────────────────────────────────────────────┤
│                                                        │
│  🔴 Critical (1)  🟡 Warning (2)  🔵 Info (0)         │
│                                                        │
│  ┌────────────────────────────────────────────────┐  │
│  │ 🔴 ARRの値に30%以上の乖離                      │  │
│  │    検出日時: 2025/10/01 11:15                 │  │
│  │    ステータス: 未解決                          │  │
│  ├────────────────────────────────────────────────┤  │
│  │ 競合する値:                                    │  │
│  │                                                │  │
│  │ ① ¥300,000,000 (3億円)                       │  │
│  │    ソース: CONF - 財務モデル                  │  │
│  │    時点: 2025/09/30                           │  │
│  │    信頼度: 100%                               │  │
│  │                                                │  │
│  │ ② ¥400,000,000 (4億円)                       │  │
│  │    ソース: INT - CEOインタビュー              │  │
│  │    時点: 2025/09/28                           │  │
│  │    信頼度: 90%                                │  │
│  │                                                │  │
│  │ 差異: 33.3%                                   │  │
│  │                                                │  │
│  │ システムの分析:                               │  │
│  │ - 時点の違い（2日差）では説明できない差異    │  │
│  │ - 定義の違いの可能性（MRR×12 vs 年契約額）   │  │
│  │                                                │  │
│  │ 推奨アクション:                               │  │
│  │ • CEOに定義を再確認                           │  │
│  │ • 財務モデルと突合                            │  │
│  │                                                │  │
│  │ [解決方法を選択]                              │  │
│  │ ○ ①を採用（CONF優先）                        │  │
│  │ ○ ②を採用（最新情報）                        │  │
│  │ ○ 両方を保持し注記                           │  │
│  │ ○ 経営陣に再確認                             │  │
│  │                                                │  │
│  │ [解決する]                                    │  │
│  └────────────────────────────────────────────────┘  │
│                                                        │
│  ┌────────────────────────────────────────────────┐  │
│  │ 🟡 従業員数のデータが古い                     │  │
│  │    最終更新: 2025/06/01 (4ヶ月前)            │  │
│  │                                                │  │
│  │    [更新を依頼]  [今は無視]                   │  │
│  └────────────────────────────────────────────────┘  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 3. 承認ワークフローの詳細設計

### 3-1. 承認が必要なポイント

```
情報収集プロセスにおける承認ポイント:

1. CONF文書からの抽出結果
   - Term Sheet の条件
   - Cap Table の株主構成
   - 財務モデルの前提

2. 重大な矛盾の解決
   - 30%以上の数値乖離
   - 論理的矛盾

3. 外部推計値の採用
   - 信頼度 < 70% のデータ
   - クリティカルパスの数値

4. 最終レポートの公開
   - IC提出前
   - LP配布前
```

### 3-2. 承認フローの実装

```python
# approval_workflow.py
from enum import Enum
from typing import Optional

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

class ApprovalRequest:
    def __init__(
        self,
        item_type: str,  # 'observation', 'conflict_resolution', 'report'
        item_id: UUID,
        case_id: UUID,
        requested_by: UUID,
        approver: UUID,
        urgency: str = "medium"
    ):
        self.id = uuid4()
        self.item_type = item_type
        self.item_id = item_id
        self.case_id = case_id
        self.requested_by = requested_by
        self.approver = approver
        self.urgency = urgency
        self.status = ApprovalStatus.PENDING
        self.created_at = datetime.now()
        self.responded_at: Optional[datetime] = None
        self.response_notes: Optional[str] = None
    
    async def approve(self, approver_id: UUID, notes: str = ""):
        """承認"""
        self.status = ApprovalStatus.APPROVED
        self.responded_at = datetime.now()
        self.response_notes = notes
        
        # 元のアイテムを承認済みとしてマーク
        await mark_item_approved(self.item_type, self.item_id, approver_id)
        
        # 通知
        await notify_requester(
            self.requested_by,
            f"Your approval request for {self.item_type} was approved"
        )
        
        # 次のステップをトリガー（ワークフローの続行）
        await trigger_next_stage(self.case_id)
    
    async def reject(self, approver_id: UUID, reason: str):
        """却下"""
        self.status = ApprovalStatus.REJECTED
        self.responded_at = datetime.now()
        self.response_notes = reason
        
        # 元のアイテムを却下としてマーク
        await mark_item_rejected(self.item_type, self.item_id, reason)
        
        # 通知
        await notify_requester(
            self.requested_by,
            f"Your approval request for {self.item_type} was rejected: {reason}"
        )
    
    async def request_revision(self, approver_id: UUID, feedback: str):
        """修正依頼"""
        self.status = ApprovalStatus.NEEDS_REVISION
        self.response_notes = feedback
        
        # タスク作成
        await create_task(
            case_id=self.case_id,
            task_type="revision",
            title=f"Revision required for {self.item_type}",
            description=feedback,
            assigned_to=self.requested_by
        )

# 使用例
async def process_conf_extraction(document_id: UUID, extracted_data: dict):
    """
    CONF文書から抽出したデータを処理
    """
    # 抽出結果を一時保存
    temp_observations = save_temp_observations(extracted_data)
    
    # 承認リクエスト作成
    approval = ApprovalRequest(
        item_type="conf_extraction",
        item_id=document_id,
        case_id=extracted_data["case_id"],
        requested_by=SYSTEM_USER_ID,
        approver=get_lead_partner(extracted_data["case_id"]),
        urgency="high"
    )
    
    await save_approval_request(approval)
    
    # 承認者に通知
    await notify_approver(
        approval.approver,
        {
            "type": "approval_required",
            "title": "Term Sheet抽出結果の確認",
            "case": extracted_data["company_name"],
            "link": f"/approvals/{approval.id}"
        }
    )
```

### 3-3. 承認の優先度とSLA

```yaml
承認のSLA（Service Level Agreement）:

Critical（緊急）:
  - 対象: IC前日の承認、重大な矛盾
  - 期限: 4時間以内
  - 通知: Slack即時 + メール + SMS

High（高）:
  - 対象: CONF抽出結果、重要な矛盾
  - 期限: 24時間以内
  - 通知: Slack + メール

Medium（中）:
  - 対象: 外部推計値の採用、一般的な矛盾
  - 期限: 3営業日以内
  - 通知: 社内通知

Low（低）:
  - 対象: 非重要項目の確認
  - 期限: 1週間以内
  - 通知: 週次ダイジェスト
```

---

## 4. インタラクティブな編集機能

### 4-1. インライン編集

```
観測データの編集:

┌────────────────────────────────────────────────────┐
│ ARR (年間経常収益)                                 │
├────────────────────────────────────────────────────┤
│ 現在の値: ¥300,000,000                            │
│                                                    │
│ [編集モード]                                      │
│                                                    │
│ 値: [¥300,000,000___________]  単位: [JPY ▼]     │
│                                                    │
│ 時点: [2025-09-30_____]                           │
│                                                    │
│ 出典: [財務モデル_____________________________]   │
│                                                    │
│ 信頼度: ━━━━━●━━━━━ 100%                        │
│                                                    │
│ 注記:                                             │
│ ┌────────────────────────────────────────────┐    │
│ │ MRR × 12で計算。解約率を考慮。              │    │
│ │                                             │    │
│ └────────────────────────────────────────────┘    │
│                                                    │
│ [保存]  [キャンセル]                              │
└────────────────────────────────────────────────────┘
```

### 4-2. バージョン管理

```python
# versioning.py
class ObservationHistory:
    """観測データの履歴管理"""
    
    @staticmethod
    async def create_version(
        observation_id: UUID,
        changes: dict,
        changed_by: UUID,
        reason: str
    ):
        """新バージョンの作成"""
        current = await get_observation(observation_id)
        
        # 現在の値を履歴に保存
        await save_to_history({
            "observation_id": observation_id,
            "version": current.version,
            "data": current.to_dict(),
            "valid_from": current.updated_at,
            "valid_to": datetime.now()
        })
        
        # 新バージョンを保存
        current.update(changes)
        current.version += 1
        current.updated_by = changed_by
        current.updated_at = datetime.now()
        
        await save_observation(current)
        
        # 監査ログ
        await audit_log(
            action="observation_updated",
            resource_id=observation_id,
            user_id=changed_by,
            details={
                "changes": changes,
                "reason": reason,
                "previous_version": current.version - 1,
                "new_version": current.version
            }
        )
    
    @staticmethod
    async def get_history(observation_id: UUID):
        """履歴の取得"""
        return await db.fetch_all(
            "SELECT * FROM observation_history WHERE observation_id = $1 ORDER BY version DESC",
            observation_id
        )
    
    @staticmethod
    async def rollback(observation_id: UUID, target_version: int, user_id: UUID):
        """過去バージョンへのロールバック"""
        history = await get_history_version(observation_id, target_version)
        
        if not history:
            raise ValueError(f"Version {target_version} not found")
        
        await create_version(
            observation_id,
            changes=history.data,
            changed_by=user_id,
            reason=f"Rollback to version {target_version}"
        )
```

---

## 5. リアルタイム更新とコラボレーション

### 5-1. WebSocketによるリアルタイム通知

```python
# websocket_server.py
from fastapi import WebSocket
from typing import Dict, Set

class ConnectionManager:
    def __init__(self):
        # case_id -> {websocket connections}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, case_id: str):
        await websocket.accept()
        
        if case_id not in self.active_connections:
            self.active_connections[case_id] = set()
        
        self.active_connections[case_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, case_id: str):
        self.active_connections[case_id].remove(websocket)
    
    async def broadcast_to_case(self, case_id: str, message: dict):
        """特定の案件を見ている全ユーザーに通知"""
        if case_id in self.active_connections:
            for connection in self.active_connections[case_id]:
                await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/cases/{case_id}")
async def websocket_endpoint(websocket: WebSocket, case_id: str):
    await manager.connect(websocket, case_id)
    try:
        while True:
            # クライアントからのメッセージを待機
            data = await websocket.receive_text()
            # 必要に応じて処理
    except WebSocketDisconnect:
        manager.disconnect(websocket, case_id)

# イベント発生時の通知例
async def on_observation_updated(case_id: str, observation: dict):
    """観測データが更新されたときに通知"""
    await manager.broadcast_to_case(case_id, {
        "type": "observation_updated",
        "observation": observation
    })

async def on_workflow_stage_completed(case_id: str, stage: str):
    """ワークフローステージが完了したときに通知"""
    await manager.broadcast_to_case(case_id, {
        "type": "stage_completed",
        "stage": stage
    })
```

### 5-2. フロントエンドでの受信

```javascript
// React コンポーネント例
import { useEffect, useState } from 'react';

function CaseDetail({ caseId }) {
  const [caseData, setCaseData] = useState(null);
  const [ws, setWs] = useState(null);
  
  useEffect(() => {
    // WebSocket接続
    const websocket = new WebSocket(`wss://api.example.com/ws/cases/${caseId}`);
    
    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      switch (message.type) {
        case 'observation_updated':
          // 観測データを更新
          updateObservation(message.observation);
          showToast('データが更新されました');
          break;
        
        case 'stage_completed':
          // ステージ完了通知
          updateWorkflowStage(message.stage);
          showToast(`${message.stage} が完了しました`);
          break;
        
        case 'conflict_detected':
          // 矛盾検出通知
          showAlert('データの矛盾が検出されました', 'warning');
          break;
      }
    };
    
    setWs(websocket);
    
    return () => {
      websocket.close();
    };
  }, [caseId]);
  
  return (
    <div>
      {/* UIコンポーネント */}
    </div>
  );
}
```

---

## 6. モバイル対応

### 6-1. レスポンシブデザイン

```
【デスクトップ】
┌──────────────────────────────────────┐
│ [サイドバー] │ [メインコンテンツ]  │
│              │                      │
│ ・ダッシュ   │   案件詳細           │
│ ・案件一覧   │   ...                │
│ ・タスク     │                      │
└──────────────────────────────────────┘

【モバイル】
┌──────────────────┐
│ [☰ Menu]  [通知] │
├──────────────────┤
│                  │
│  案件詳細        │
│                  │
│  ...             │
│                  │
│                  │
└──────────────────┘
```

### 6-2. 承認専用モバイルアプリ

```
パートナー向けの承認専用アプリ:

機能:
- プッシュ通知による承認依頼
- ワンタップ承認/却下
- 簡易コメント入力
- オフライン対応（キューイング）

技術スタック:
- React Native / Flutter
- Firebase Cloud Messaging（プッシュ通知）
- オフラインストレージ（SQLite）
```

---

このUI設計と承認フローにより、効率的で使いやすいシステムを構築できます。次のセクションでは、運用・保守計画と費用対効果分析について詳述します。

