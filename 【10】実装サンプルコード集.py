# =============================================================================
# ファンドIC資料自動化システム - 実装サンプルコード集
# =============================================================================

import logging
from typing import Dict, List, Optional, TypedDict, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import uuid
import json

# ロギング設定
logger = logging.getLogger(__name__)

# =============================================================================
# 型定義（TypedDict）
# =============================================================================

class ObservationData(TypedDict, total=False):
    """観測データの型定義"""
    id: str
    section: str
    field: str
    value_type: str
    value_number: Optional[float]
    value_string: Optional[str]
    value_date: Optional[datetime]
    value_boolean: Optional[bool]
    value_json: Optional[Dict[str, Any]]
    unit: Optional[str]
    source_tag: str  # PUB, EXT, INT, CONF, ANL
    evidence: str
    as_of: datetime
    confidence: float
    disclosure_level: str
    requires_approval: bool
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    notes: Optional[str]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

class CaseData(TypedDict, total=False):
    """案件データの型定義"""
    id: str
    company_name: str
    stage: str  # seed, early, growth, late
    status: str
    location: Optional[str]
    founded_date: Optional[datetime]
    website_url: Optional[str]
    lead_partner_id: Optional[str]
    analyst_id: Optional[str]
    discovered_at: datetime
    ic_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class ConflictData(TypedDict, total=False):
    """矛盾検出結果の型定義"""
    field: str
    observation_ids: List[str]
    deviation_pct: float
    severity: str  # critical, warning, info
    conflict_type: str
    details: Dict[str, Any]

class ResolutionData(TypedDict, total=False):
    """矛盾解決結果の型定義"""
    resolution: str
    reason: str
    selected: Optional[str]

class CalculationData(TypedDict, total=False):
    """計算結果の型定義"""
    calc_type: str
    value: Union[float, str]
    unit: Optional[str]
    calculated_at: datetime

# =============================================================================
# 0. 設定クラス
# =============================================================================

@dataclass
class Config:
    """アプリケーション設定（マジックナンバーの一元管理）"""
    # データ処理
    MAX_CONTENT_LENGTH = 10000
    DEFAULT_CONFIDENCE = 0.9

    # 矛盾検出
    CONFLICT_THRESHOLD_PCT = 10
    SEVERITY_WARNING_PCT = 15
    SEVERITY_CRITICAL_PCT = 30

    # ウェブスクレイピング
    PLAYWRIGHT_TIMEOUT_MS = 30000
    UNWANTED_HTML_TAGS = ['script', 'style', 'nav', 'footer', 'iframe', 'noscript']

    # リトライ設定
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 2  # 秒
    RETRY_BACKOFF_FACTOR = 2  # 指数バックオフ
    MAX_RETRY_DELAY = 30  # 秒

    # LLM設定
    LLM_MODEL = "gpt-4o"
    LLM_TEMPERATURE_EXTRACTION = 0.1
    LLM_TEMPERATURE_GENERATION = 0.3

# =============================================================================
# 1. データモデル（SQLAlchemy）
# =============================================================================

from sqlalchemy import Column, String, DateTime, Float, JSON, ForeignKey, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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

# =============================================================================
# 1.5. リトライロジックとエラーハンドリング
# =============================================================================

class RetryableError(Exception):
    """リトライ可能なエラーの基底クラス"""
    pass

class RateLimitError(RetryableError):
    """API レート制限エラー"""
    pass

class TemporaryError(RetryableError):
    """一時的なエラー（タイムアウトなど）"""
    pass

class RetryHandler:
    """リトライロジックの統一管理"""

    def __init__(self, config: Config = None):
        self.config = config or Config()

    async def execute_with_retry(
        self,
        func,
        *args,
        **kwargs
    ):
        """非同期関数をリトライロジック付きで実行"""
        attempt = 0
        last_error = None

        while attempt < self.config.MAX_RETRIES:
            try:
                logger.debug(f"Executing {func.__name__} (attempt {attempt + 1}/{self.config.MAX_RETRIES})")
                return await func(*args, **kwargs)

            except RetryableError as e:
                last_error = e
                attempt += 1

                if attempt < self.config.MAX_RETRIES:
                    delay = min(
                        self.config.INITIAL_RETRY_DELAY * (self.config.RETRY_BACKOFF_FACTOR ** (attempt - 1)),
                        self.config.MAX_RETRY_DELAY
                    )
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}): {e}. "
                        f"Retrying in {delay:.1f} seconds..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"{func.__name__} failed after {self.config.MAX_RETRIES} attempts: {e}"
                    )

            except Exception as e:
                # リトライ不可のエラーは即座に失敗
                logger.error(f"Non-retryable error in {func.__name__}: {e}")
                raise

        # すべてのリトライが失敗した場合
        raise last_error or Exception(f"Failed to execute {func.__name__}")


class LLMService:
    """LLM API呼び出しの共通化（テンプレートメソッドパターン）"""

    def __init__(self, api_key: str, config: Config = None):
        self.config = config or Config()
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.retry_handler = RetryHandler(self.config)

    async def call_extraction(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Dict:
        """JSON形式での情報抽出（構造化出力）"""
        return await self.retry_handler.execute_with_retry(
            self._call_llm,
            system_prompt,
            user_prompt,
            response_format={"type": "json_object"},
            temperature=self.config.LLM_TEMPERATURE_EXTRACTION
        )

    async def call_generation(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> str:
        """テキスト生成"""
        return await self.retry_handler.execute_with_retry(
            self._call_llm,
            system_prompt,
            user_prompt,
            response_format=None,
            temperature=self.config.LLM_TEMPERATURE_GENERATION
        )

    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[Dict] = None,
        temperature: float = 0.1
    ):
        """LLM API呼び出しの共通ロジック"""
        try:
            response = await self.client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=response_format,
                temperature=temperature
            )

            # 抽出の場合はJSON、生成の場合はテキストを返す
            content = response.choices[0].message.content
            if response_format and response_format.get("type") == "json_object":
                return json.loads(content)
            return content

        except openai.RateLimitError as e:
            raise RateLimitError(f"Rate limit exceeded: {e}") from e
        except openai.APIError as e:
            raise TemporaryError(f"LLM API error: {e}") from e
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise TemporaryError(f"Invalid response format: {e}") from e

# =============================================================================
# 2. PUB収集エージェント
# =============================================================================

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import openai

class PUBCollector:
    """公開情報（PUB）収集エージェント"""

    def __init__(self, openai_api_key: str, config: Config = None):
        self.config = config or Config()
        self.llm_service = LLMService(openai_api_key, self.config)
        self.retry_handler = RetryHandler(self.config)
        self.extraction_prompt = self._build_extraction_prompt()

    async def collect_from_website(self, url: str) -> List[ObservationData]:
        """企業WebサイトからPUB情報を収集（リトライロジック付き）"""
        try:
            # 1. Webページを取得（リトライ対応）
            html_content = await self.retry_handler.execute_with_retry(
                self._fetch_webpage,
                url
            )

            # 2. HTMLをクリーニング
            clean_text = await asyncio.to_thread(self._clean_html, html_content)

            # 3. LLMで情報抽出（リトライ対応）
            extracted_data = await self.retry_handler.execute_with_retry(
                self._extract_with_llm,
                clean_text,
                url
            )

            # 4. 観測データ形式に変換
            observations = self._to_observations(extracted_data, url)

            logger.info(f"Successfully collected {len(observations)} observations from {url}")
            return observations

        except Exception as e:
            logger.error(f"Failed to collect from {url}: {e}")
            raise

    async def _fetch_webpage(self, url: str) -> str:
        """Playwrightでページを取得"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until="networkidle", timeout=self.config.PLAYWRIGHT_TIMEOUT_MS)
                html = await page.content()
                logger.debug(f"Successfully fetched {url}")
                return html
            except asyncio.TimeoutError as e:
                raise TemporaryError(f"Timeout fetching {url}: {e}") from e
            except Exception as e:
                raise TemporaryError(f"Error fetching {url}: {e}") from e
            finally:
                await browser.close()

    def _clean_html(self, html: str) -> str:
        """HTMLから不要要素を削除してテキスト化"""
        soup = BeautifulSoup(html, 'html.parser')

        # 不要なタグを削除（設定から取得）
        for tag in soup(self.config.UNWANTED_HTML_TAGS):
            tag.decompose()

        # テキスト抽出
        text = soup.get_text(separator='\n', strip=True)

        # 連続する空行を削除
        lines = [line for line in text.split('\n') if line.strip()]
        clean_text = '\n'.join(lines)

        # トークン制限対策
        return clean_text[:self.config.MAX_CONTENT_LENGTH]
    
    async def _extract_with_llm(self, content: str, url: str) -> Dict:
        """LLMで情報抽出（LLMService経由、リトライ対応）"""
        user_prompt = f"URL: {url}\n\nコンテンツ:\n{content}"
        result = await self.llm_service.call_extraction(
            self.extraction_prompt,
            user_prompt
        )
        logger.debug(f"Successfully extracted data from {url}")
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
            # デフォルト信頼度を設定から取得
            confidence = data.get(f"{field}_confidence", self.config.DEFAULT_CONFIDENCE)

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

# =============================================================================
# 3. 正規化・矛盾検出エンジン（Strategyパターン）
# =============================================================================

from collections import defaultdict
from abc import ABC, abstractmethod

class ConflictDetectionStrategy(ABC):
    """矛盾検出戦略の基底クラス"""

    @abstractmethod
    def can_detect(self, observations: List[ObservationData]) -> bool:
        """この戦略で検出可能か判定"""
        pass

    @abstractmethod
    def detect(self, observations: List[ObservationData]) -> List[ConflictData]:
        """矛盾を検出"""
        pass


class NumericConflictStrategy(ConflictDetectionStrategy):
    """数値フィールドの矛盾検出戦略"""

    def __init__(self, config: Config = None):
        self.config = config or Config()

    def can_detect(self, observations: List[ObservationData]) -> bool:
        """数値フィールドが含まれているか"""
        return any(obs.get('value_number') is not None for obs in observations)

    def detect(self, observations: List[ObservationData]) -> List[ConflictData]:
        """数値フィールドの矛盾を検出"""
        conflicts: List[ConflictData] = []

        for obs in observations:
            if obs.get('value_number') is not None:
                conflict = self._check_numeric_conflict(obs)
                if conflict:
                    conflicts.append(conflict)

        return conflicts

    def _check_numeric_conflict(self, observation: ObservationData) -> Optional[ConflictData]:
        """単一の数値フィールドの矛盾をチェック"""
        # 実装は後のメソッドに委譲
        pass


class ConflictResolver(ABC):
    """矛盾解決戦略の基底クラス"""

    @abstractmethod
    def resolve(
        self,
        conflict: ConflictData,
        observations: List[ObservationData]
    ) -> ResolutionData:
        """矛盾を解決"""
        pass


class SourcePriorityResolver(ConflictResolver):
    """ソース優先度に基づく矛盾解決"""

    SOURCE_PRIORITY = {
        "CONF": 4,
        "INT": 3,
        "PUB": 2,
        "EXT": 1,
        "ANL": 0
    }

    def __init__(self, config: Config = None):
        self.config = config or Config()

    def resolve(
        self,
        conflict: ConflictData,
        observations: List[ObservationData]
    ) -> ResolutionData:
        """ソース優先度で矛盾を解決"""

        obs_dict = {obs['id']: obs for obs in observations}
        conflict_obs = [obs_dict[id] for id in conflict['observation_ids']]

        # ソースの優先度で選択
        best_obs = max(conflict_obs, key=lambda o: self.SOURCE_PRIORITY.get(o['source_tag'], 0))

        # 差異が説明可能か判定
        if self._is_explainable(conflict, conflict_obs):
            resolution: ResolutionData = {
                "resolution": "keep_both",
                "reason": "時点の違いまたは定義の違いの可能性",
                "selected": None
            }
        else:
            resolution: ResolutionData = {
                "resolution": "use_highest_priority",
                "reason": f"最も信頼できるソース（{best_obs['source_tag']}）を採用",
                "selected": best_obs['id']
            }

        logger.debug(f"Resolved conflict {conflict['field']}: {resolution['resolution']}")
        return resolution

    def _is_explainable(
        self,
        conflict: ConflictData,
        observations: List[ObservationData]
    ) -> bool:
        """差異が時点や定義の違いで説明可能か判定"""

        # 時点が異なるか確認
        dates = [obs['as_of'] for obs in observations]
        if len(set(dates)) > 1:
            # 時点が異なり、かつ差異が重要度閾値未満なら説明可能
            return conflict['deviation_pct'] < self.config.SEVERITY_CRITICAL_PCT

        return False


class ConflictDetector:
    """データ矛盾検出エンジン（ファサード）

    複数の検出戦略と解決戦略を統合管理
    """

    def __init__(self, config: Config = None):
        self.config = config or Config()
        # 検出戦略を登録
        self.detection_strategies: List[ConflictDetectionStrategy] = [
            NumericConflictStrategy(self.config)
        ]
        # 解決戦略を設定
        self.resolver: ConflictResolver = SourcePriorityResolver(self.config)

    def detect_conflicts(self, observations: List[ObservationData]) -> List[ConflictData]:
        """複数の戦略を使用して矛盾を検出"""

        # フィールドごとにグループ化
        grouped = defaultdict(list)
        for obs in observations:
            key = f"{obs['section']}:{obs['field']}"
            grouped[key].append(obs)

        conflicts: List[ConflictData] = []

        # 各フィールドグループに対して検出戦略を適用
        for key, obs_list in grouped.items():
            if len(obs_list) <= 1:
                continue  # 単一ソースなら矛盾なし

            # 適用可能な戦略を探す
            for strategy in self.detection_strategies:
                if strategy.can_detect(obs_list):
                    strategy_conflicts = strategy.detect(obs_list)
                    conflicts.extend(strategy_conflicts)

        logger.info(f"Detected {len(conflicts)} conflicts among {len(observations)} observations")
        return conflicts

    def auto_resolve(
        self,
        conflict: ConflictData,
        observations: List[ObservationData]
    ) -> ResolutionData:
        """矛盾を自動解決"""
        return self.resolver.resolve(conflict, observations)

    def add_detection_strategy(self, strategy: ConflictDetectionStrategy) -> None:
        """新しい検出戦略を追加"""
        self.detection_strategies.append(strategy)
        logger.info(f"Added detection strategy: {strategy.__class__.__name__}")

    def set_resolver(self, resolver: ConflictResolver) -> None:
        """解決戦略を変更"""
        self.resolver = resolver
        logger.info(f"Changed resolver to: {resolver.__class__.__name__}")

# =============================================================================
# 4. レポート生成エンジン
# =============================================================================

from jinja2 import Template

class ReportGenerator:
    """IC資料生成エンジン"""

    def __init__(self, openai_api_key: str, config: Config = None):
        self.config = config or Config()
        self.llm_service = LLMService(openai_api_key, self.config)

    async def generate_ic_report(
        self,
        case_data: CaseData,
        observations: List[ObservationData],
        calculations: List[CalculationData]
    ) -> str:
        """IC資料のMarkdownを生成"""

        try:
            # セクションごとに情報を整理
            sections = self._organize_sections(observations, calculations)

            # 各セクションの本文を生成（LLMService経由、リトライ対応）
            for section in sections:
                section['content'] = await self._generate_section_content(
                    section['title'],
                    section['data'],
                    case_data
                )

            # Markdownテンプレートで最終化
            markdown = self._render_markdown(case_data, sections)

            logger.info(f"Successfully generated IC report for {case_data['company_name']}")
            return markdown

        except Exception as e:
            logger.error(f"Failed to generate IC report for {case_data['company_name']}: {e}")
            raise
    
    def _organize_sections(
        self,
        observations: List[ObservationData],
        calculations: List[CalculationData]
    ) -> List[Dict[str, Any]]:
        """セクション構成を組み立て"""

        sections: List[Dict[str, Any]] = [
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
        """セクションの本文をLLMで生成（LLMService経由、リトライ対応）"""

        system_prompt = "あなたはベンチャーキャピタルのアナリストです。"

        user_prompt = f"""投資委員会資料の「{section_title}」セクションを作成してください。

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

        content = await self.llm_service.call_generation(system_prompt, user_prompt)
        logger.debug(f"Generated content for section '{section_title}'")
        return content
    
    def _render_markdown(self, case_data: CaseData, sections: List[Dict[str, Any]]) -> str:
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
    """バックグラウンドタスク：PUB情報収集（リトライロジック付き）"""
    try:
        collector = PUBCollector(openai_api_key="YOUR_API_KEY")
        observations = await collector.collect_from_website(url)

        # DBに保存
        for obs in observations:
            obs['case_id'] = case_id
            # await db.observations.insert(obs)

        logger.info(f"PUB collection completed for case {case_id}: {len(observations)} observations")

    except RetryableError as e:
        logger.error(f"Retryable error collecting PUB info for case {case_id}: {e}")
        # エラー通知を送信（リトライ失敗）

    except Exception as e:
        logger.error(f"Non-retryable error collecting PUB info for case {case_id}: {e}")
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
