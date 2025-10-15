# =============================================================================
# ファンドIC資料自動化システム - 実装サンプルコード集
# =============================================================================

# -----------------------------------------------------------------------------
# 1. データモデル（SQLAlchemy）
# -----------------------------------------------------------------------------

from sqlalchemy import Column, String, DateTime, Float, JSON, ForeignKey, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Case(Base):
    """案件マスター"""
    __tablename__ = "cases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False, index=True)
    stage = Column(String(50), nullable=False, index=True)  # seed, early, growth, late
    status = Column(String(50), nullable=False, default='draft', index=True)
    
    location = Column(String(255))
    founded_date = Column(DateTime)
    website_url = Column(Text)
    
    lead_partner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    analyst_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    discovered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ic_date = Column(DateTime)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    observations = relationship("Observation", back_populates="case", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="case")

class Observation(Base):
    """観測データ（すべての情報の単一ソース）"""
    __tablename__ = "observations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey('cases.id', ondelete='CASCADE'), nullable=False, index=True)
    
    section = Column(String(100), nullable=False, index=True)
    field = Column(String(100), nullable=False, index=True)
    
    # 値（型に応じて使い分け）
    value_type = Column(String(50), nullable=False)
    value_number = Column(Float)
    value_string = Column(Text)
    value_date = Column(DateTime)
    value_boolean = Column(Boolean)
    value_json = Column(JSONB)
    
    unit = Column(String(50))
    
    source_tag = Column(String(10), nullable=False, index=True)  # PUB, EXT, INT, CONF, ANL
    evidence = Column(Text, nullable=False)
    as_of = Column(DateTime, nullable=False)
    
    confidence = Column(Float)
    disclosure_level = Column(String(20), nullable=False, default='IC')
    
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approved_at = Column(DateTime)
    
    notes = Column(Text)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    case = relationship("Case", back_populates="observations")

# -----------------------------------------------------------------------------
# 2. PUB収集エージェント
# -----------------------------------------------------------------------------

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import openai
import json
from typing import List, Dict

class PUBCollector:
    """公開情報（PUB）収集エージェント"""
    
    def __init__(self, openai_api_key: str):
        self.llm = openai.AsyncOpenAI(api_key=openai_api_key)
        self.extraction_prompt = self._build_extraction_prompt()
    
    async def collect_from_website(self, url: str) -> List[Dict]:
        """企業WebサイトからPUB情報を収集"""
        
        # 1. Webページを取得
        html_content = await self._fetch_webpage(url)
        
        # 2. HTMLをクリーニング
        clean_text = self._clean_html(html_content)
        
        # 3. LLMで情報抽出
        extracted_data = await self._extract_with_llm(clean_text, url)
        
        # 4. 観測データ形式に変換
        observations = self._to_observations(extracted_data, url)
        
        return observations
    
    async def _fetch_webpage(self, url: str) -> str:
        """Playwrightでページを取得"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                html = await page.content()
            finally:
                await browser.close()
            
            return html
    
    def _clean_html(self, html: str) -> str:
        """HTMLから不要要素を削除してテキスト化"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 不要なタグを削除
        for tag in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript']):
            tag.decompose()
        
        # テキスト抽出
        text = soup.get_text(separator='\n', strip=True)
        
        # 連続する空行を削除
        lines = [line for line in text.split('\n') if line.strip()]
        clean_text = '\n'.join(lines)
        
        return clean_text[:10000]  # トークン制限対策
    
    async def _extract_with_llm(self, content: str, url: str) -> Dict:
        """LLMで情報抽出"""
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.extraction_prompt},
                {"role": "user", "content": f"URL: {url}\n\nコンテンツ:\n{content}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    
    def _to_observations(self, data: Dict, source_url: str) -> List[Dict]:
        """抽出データを観測データ形式に変換"""
        observations = []
        
        field_mapping = {
            "company_name": ("basic_info", "company_name"),
            "location": ("basic_info", "location"),
            "founded_date": ("basic_info", "founded_date"),
            "employee_count": ("team", "employee_count"),
            "business_description": ("basic_info", "business_description"),
        }
        
        for field, value in data.items():
            if field.endswith("_confidence"):
                continue  # 信頼度フィールドはスキップ
            
            if value is None or value == "":
                continue
            
            section, field_name = field_mapping.get(field, ("other", field))
            confidence = data.get(f"{field}_confidence", 0.9)
            
            obs = {
                "section": section,
                "field": field_name,
                "value": value,
                "source_tag": "PUB",
                "evidence": source_url,
                "as_of": datetime.utcnow(),
                "confidence": confidence,
                "disclosure_level": "IC"
            }
            
            observations.append(obs)
        
        return observations
    
    def _build_extraction_prompt(self) -> str:
        """抽出用プロンプトを構築"""
        return """あなたはベンチャーキャピタルのリサーチアナリストです。
企業のWebサイトから投資判断に必要な情報を正確に抽出してください。

【重要な制約】
1. 事実のみを抽出し、推測は行わない
2. 不明な項目はnullとする
3. 数値には必ず単位を含める
4. 信頼度（0.0-1.0）を各項目に付与

【抽出項目】
- company_name: 会社名
- location: 所在地（都道府県・市区まで）
- founded_date: 設立年月日（YYYY-MM-DD形式）
- employee_count: 従業員数（数値のみ）
- business_description: 事業内容（100文字以内）
- management_team: 経営陣（配列、名前と役職）

【出力形式】
必ず以下のJSON形式で出力してください：
{
  "company_name": "株式会社サンプル",
  "company_name_confidence": 1.0,
  "location": "東京都渋谷区",
  "location_confidence": 0.95,
  ...
}"""

# -----------------------------------------------------------------------------
# 3. 正規化・矛盾検出エンジン
# -----------------------------------------------------------------------------

from collections import defaultdict
from typing import List, Dict, Tuple

class ConflictDetector:
    """データ矛盾検出エンジン"""
    
    def __init__(self):
        self.source_priority = {
            "CONF": 4,
            "INT": 3,
            "PUB": 2,
            "EXT": 1,
            "ANL": 0
        }
    
    def detect_conflicts(self, observations: List[Dict]) -> List[Dict]:
        """同一フィールドの矛盾を検出"""
        
        # フィールドごとにグループ化
        grouped = defaultdict(list)
        for obs in observations:
            key = f"{obs['section']}:{obs['field']}"
            grouped[key].append(obs)
        
        conflicts = []
        
        for key, obs_list in grouped.items():
            if len(obs_list) <= 1:
                continue  # 単一ソースなら矛盾なし
            
            # 数値フィールドの場合、差異を計算
            if obs_list[0].get('value_number') is not None:
                conflict = self._check_numeric_conflict(key, obs_list)
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def _check_numeric_conflict(self, field_key: str, observations: List[Dict]) -> Dict:
        """数値フィールドの矛盾をチェック"""
        
        values = [(obs['value_number'], obs) for obs in observations]
        values.sort(key=lambda x: x[0])  # 値でソート
        
        min_val, min_obs = values[0]
        max_val, max_obs = values[-1]
        
        # 差異率を計算
        if min_val == 0:
            deviation_pct = float('inf') if max_val > 0 else 0
        else:
            deviation_pct = abs((max_val - min_val) / min_val) * 100
        
        # 10%以上の差異があれば矛盾とみなす
        if deviation_pct < 10:
            return None
        
        # 重要度判定
        if deviation_pct >= 30:
            severity = "critical"
        elif deviation_pct >= 15:
            severity = "warning"
        else:
            severity = "info"
        
        return {
            "field": field_key,
            "observation_ids": [obs['id'] for obs in observations],
            "deviation_pct": round(deviation_pct, 2),
            "severity": severity,
            "conflict_type": "value",
            "details": {
                "min": {"value": min_val, "source": min_obs['source_tag']},
                "max": {"value": max_val, "source": max_obs['source_tag']}
            }
        }
    
    def auto_resolve(self, conflict: Dict, observations: List[Dict]) -> Dict:
        """矛盾を自動解決（可能な場合）"""
        
        obs_dict = {obs['id']: obs for obs in observations}
        conflict_obs = [obs_dict[id] for id in conflict['observation_ids']]
        
        # ソースの優先度で選択
        best_obs = max(conflict_obs, key=lambda o: self.source_priority.get(o['source_tag'], 0))
        
        # 差異が説明可能か判定
        if self._is_explainable(conflict, conflict_obs):
            return {
                "resolution": "keep_both",
                "reason": "時点の違いまたは定義の違いの可能性",
                "selected": None
            }
        else:
            return {
                "resolution": "use_highest_priority",
                "reason": f"最も信頼できるソース（{best_obs['source_tag']}）を採用",
                "selected": best_obs['id']
            }
    
    def _is_explainable(self, conflict: Dict, observations: List[Dict]) -> bool:
        """差異が時点や定義の違いで説明可能か判定"""
        
        # 時点が異なるか確認
        dates = [obs['as_of'] for obs in observations]
        if len(set(dates)) > 1:
            # 時点が異なり、かつ差異が30%未満なら説明可能
            return conflict['deviation_pct'] < 30
        
        return False

# -----------------------------------------------------------------------------
# 4. レポート生成エンジン
# -----------------------------------------------------------------------------

from jinja2 import Template
from typing import Dict, List

class ReportGenerator:
    """IC資料生成エンジン"""
    
    def __init__(self, openai_api_key: str):
        self.llm = openai.AsyncOpenAI(api_key=openai_api_key)
    
    async def generate_ic_report(
        self, 
        case_data: Dict,
        observations: List[Dict],
        calculations: List[Dict]
    ) -> str:
        """IC資料のMarkdownを生成"""
        
        # セクションごとに情報を整理
        sections = self._organize_sections(observations, calculations)
        
        # 各セクションの本文を生成
        for section in sections:
            section['content'] = await self._generate_section_content(
                section['title'],
                section['data'],
                case_data
            )
        
        # Markdownテンプレートで最終化
        markdown = self._render_markdown(case_data, sections)
        
        return markdown
    
    def _organize_sections(self, observations: List[Dict], calculations: List[Dict]) -> List[Dict]:
        """セクション構成を組み立て"""
        
        sections = [
            {"title": "概要", "fields": ["company_name", "location", "founded_date"]},
            {"title": "課題", "fields": ["problem", "customer_pain"]},
            {"title": "解決策", "fields": ["solution", "product"]},
            {"title": "市場規模", "fields": ["tam", "sam", "som"]},
            {"title": "ビジネスモデル", "fields": ["revenue_model", "arr", "mrr"]},
        ]
        
        # 各セクションにデータを紐付け
        obs_by_field = {obs['field']: obs for obs in observations}
        calc_by_type = {calc['calc_type']: calc for calc in calculations}
        
        for section in sections:
            section['data'] = {}
            for field in section['fields']:
                if field in obs_by_field:
                    section['data'][field] = obs_by_field[field]
                elif field in calc_by_type:
                    section['data'][field] = calc_by_type[field]
        
        return sections
    
    async def _generate_section_content(
        self,
        section_title: str,
        data: Dict,
        case_data: Dict
    ) -> str:
        """セクションの本文をLLMで生成"""
        
        prompt = f"""投資委員会資料の「{section_title}」セクションを作成してください。

企業名: {case_data['company_name']}
ステージ: {case_data['stage']}

利用可能なデータ:
{json.dumps(data, ensure_ascii=False, indent=2)}

要件:
- 簡潔で明確な記述
- データに基づく事実のみ記載
- 投資判断に役立つ洞察
- 500文字以内

Markdown形式で出力してください。"""
        
        response = await self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたはベンチャーキャピタルのアナリストです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    def _render_markdown(self, case_data: Dict, sections: List[Dict]) -> str:
        """最終的なMarkdownを生成"""
        
        template = Template("""
# {{ company_name }}
投資委員会資料

**作成日:** {{ date }}
**ステージ:** {{ stage }}

---

{% for section in sections %}
## {{ section.title }}

{{ section.content }}

{% endfor %}

---

*このレポートは自動生成されました。最終判断の前に必ず内容を確認してください。*
""")
        
        return template.render(
            company_name=case_data['company_name'],
            date=datetime.utcnow().strftime('%Y-%m-%d'),
            stage=case_data['stage'],
            sections=sections
        )

# -----------------------------------------------------------------------------
# 5. FastAPI エンドポイント例
# -----------------------------------------------------------------------------

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Fund IC Automation API")
security = HTTPBearer()

# リクエスト/レスポンスモデル
class CaseCreate(BaseModel):
    company_name: str
    stage: str
    location: Optional[str] = None
    website_url: Optional[str] = None

class CaseResponse(BaseModel):
    id: str
    company_name: str
    stage: str
    status: str
    created_at: str

# 依存性注入
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # JWT検証ロジック（実装は省略）
    token = credentials.credentials
    # ... JWT検証 ...
    return {"id": "user123", "email": "analyst@fund.com"}

# エンドポイント
@app.post("/api/v1/cases", response_model=CaseResponse)
async def create_case(
    case: CaseCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """新規案件の作成とPUB収集の開始"""
    
    # データベースに案件を作成
    new_case = {
        "id": str(uuid.uuid4()),
        "company_name": case.company_name,
        "stage": case.stage,
        "status": "draft",
        "lead_partner_id": current_user['id'],
        "created_at": datetime.utcnow().isoformat()
    }
    
    # DBに保存（実装は省略）
    # await db.cases.insert(new_case)
    
    # バックグラウンドでPUB収集を開始
    if case.website_url:
        background_tasks.add_task(
            collect_pub_info,
            case_id=new_case['id'],
            url=case.website_url
        )
    
    return CaseResponse(**new_case)

async def collect_pub_info(case_id: str, url: str):
    """バックグラウンドタスク：PUB情報収集"""
    try:
        collector = PUBCollector(openai_api_key="YOUR_API_KEY")
        observations = await collector.collect_from_website(url)
        
        # DBに保存
        for obs in observations:
            obs['case_id'] = case_id
            # await db.observations.insert(obs)
        
        print(f"PUB collection completed for case {case_id}: {len(observations)} observations")
    
    except Exception as e:
        print(f"Error collecting PUB info: {e}")
        # エラー通知を送信

# -----------------------------------------------------------------------------
# 6. 使用例
# -----------------------------------------------------------------------------

async def main():
    """使用例"""
    
    # PUB収集
    collector = PUBCollector(openai_api_key="YOUR_API_KEY")
    observations = await collector.collect_from_website("https://example-startup.com")
    print(f"Collected {len(observations)} observations")
    
    # 矛盾検出
    detector = ConflictDetector()
    conflicts = detector.detect_conflicts(observations)
    print(f"Detected {len(conflicts)} conflicts")
    
    # レポート生成
    generator = ReportGenerator(openai_api_key="YOUR_API_KEY")
    case_data = {"company_name": "サンプル株式会社", "stage": "early"}
    report = await generator.generate_ic_report(case_data, observations, [])
    print(report)

if __name__ == "__main__":
    asyncio.run(main())
