// C: データフローページ - 全体像の可視化
import Layout from '../components/Layout/Layout'
import {
  DocumentTextIcon,
  CloudArrowUpIcon,
  CpuChipIcon,
  CircleStackIcon,
  DocumentChartBarIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  SparklesIcon,
  GlobeAltIcon,
  TableCellsIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'

export default function DataFlow() {
  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* ヘッダー */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-secondary-900">データフロー</h1>
          <p className="mt-2 text-secondary-500 max-w-2xl mx-auto">
            資料入力からICレポート生成までの全体像
          </p>
        </div>

        {/* メインフロー図 */}
        <div className="bg-white rounded-3xl shadow-xl ring-1 ring-secondary-900/5 p-8 mb-12 overflow-x-auto">
          <div className="flex items-center justify-between min-w-[900px]">
            {/* Phase 1: 入力 */}
            <div className="flex-1">
              <div className="text-center mb-4">
                <span className="inline-flex items-center px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-sm font-medium">
                  Phase 1: 入力
                </span>
              </div>
              <div className="bg-gradient-to-br from-blue-50 to-white rounded-2xl border border-blue-200 p-6">
                <div className="flex items-center justify-center gap-2 mb-4">
                  <CloudArrowUpIcon className="h-8 w-8 text-blue-600" />
                  <h3 className="text-lg font-semibold text-secondary-900">資料アップロード</h3>
                </div>
                <div className="space-y-2">
                  {[
                    { icon: GlobeAltIcon, label: 'HP / LP', tag: 'PUB' },
                    { icon: DocumentTextIcon, label: 'PDF資料', tag: 'PUB' },
                    { icon: TableCellsIcon, label: 'Excel/CSV', tag: 'CONF' },
                    { icon: UserGroupIcon, label: 'インタビュー', tag: 'INT' },
                  ].map((item, i) => (
                    <div key={i} className="flex items-center justify-between p-2 bg-white rounded-lg shadow-sm">
                      <div className="flex items-center gap-2">
                        <item.icon className="h-4 w-4 text-secondary-500" />
                        <span className="text-sm text-secondary-700">{item.label}</span>
                      </div>
                      <span className={`text-xs px-1.5 py-0.5 rounded ${
                        item.tag === 'PUB' ? 'bg-blue-100 text-blue-700' :
                        item.tag === 'CONF' ? 'bg-rose-100 text-rose-700' :
                        'bg-amber-100 text-amber-700'
                      }`}>
                        {item.tag}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 矢印 */}
            <div className="flex-shrink-0 px-4">
              <ArrowRightIcon className="h-8 w-8 text-secondary-300" />
            </div>

            {/* Phase 2: 処理 */}
            <div className="flex-1">
              <div className="text-center mb-4">
                <span className="inline-flex items-center px-3 py-1 rounded-full bg-purple-100 text-purple-700 text-sm font-medium">
                  Phase 2: AI処理
                </span>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-white rounded-2xl border border-purple-200 p-6">
                <div className="flex items-center justify-center gap-2 mb-4">
                  <CpuChipIcon className="h-8 w-8 text-purple-600" />
                  <h3 className="text-lg font-semibold text-secondary-900">データ抽出・変換</h3>
                </div>
                <div className="space-y-2">
                  {[
                    { label: 'テキスト認識 (OCR)', icon: SparklesIcon },
                    { label: '構造化データ変換', icon: ArrowPathIcon },
                    { label: 'フィールドマッピング', icon: CircleStackIcon },
                    { label: '矛盾検出', icon: ShieldCheckIcon },
                  ].map((item, i) => (
                    <div key={i} className="flex items-center gap-2 p-2 bg-white rounded-lg shadow-sm">
                      <item.icon className="h-4 w-4 text-purple-500" />
                      <span className="text-sm text-secondary-700">{item.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 矢印 */}
            <div className="flex-shrink-0 px-4">
              <ArrowRightIcon className="h-8 w-8 text-secondary-300" />
            </div>

            {/* Phase 3: 格納 */}
            <div className="flex-1">
              <div className="text-center mb-4">
                <span className="inline-flex items-center px-3 py-1 rounded-full bg-emerald-100 text-emerald-700 text-sm font-medium">
                  Phase 3: 格納
                </span>
              </div>
              <div className="bg-gradient-to-br from-emerald-50 to-white rounded-2xl border border-emerald-200 p-6">
                <div className="flex items-center justify-center gap-2 mb-4">
                  <CircleStackIcon className="h-8 w-8 text-emerald-600" />
                  <h3 className="text-lg font-semibold text-secondary-900">データベース</h3>
                </div>
                <div className="space-y-2">
                  {[
                    { label: '36+ フィールド定義', count: '36' },
                    { label: '開示レベル管理', count: '4' },
                    { label: 'ソースタグ管理', count: '5' },
                    { label: '監査ログ', count: '∞' },
                  ].map((item, i) => (
                    <div key={i} className="flex items-center justify-between p-2 bg-white rounded-lg shadow-sm">
                      <span className="text-sm text-secondary-700">{item.label}</span>
                      <span className="text-xs font-medium text-emerald-600">{item.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 矢印 */}
            <div className="flex-shrink-0 px-4">
              <ArrowRightIcon className="h-8 w-8 text-secondary-300" />
            </div>

            {/* Phase 4: 出力 */}
            <div className="flex-1">
              <div className="text-center mb-4">
                <span className="inline-flex items-center px-3 py-1 rounded-full bg-amber-100 text-amber-700 text-sm font-medium">
                  Phase 4: 出力
                </span>
              </div>
              <div className="bg-gradient-to-br from-amber-50 to-white rounded-2xl border border-amber-200 p-6">
                <div className="flex items-center justify-center gap-2 mb-4">
                  <DocumentChartBarIcon className="h-8 w-8 text-amber-600" />
                  <h3 className="text-lg font-semibold text-secondary-900">レポート生成</h3>
                </div>
                <div className="space-y-2">
                  {[
                    { label: 'IC資料（フル版）', tag: 'IC' },
                    { label: 'LP資料（マスク版）', tag: 'LP' },
                    { label: 'LP資料（NDA版）', tag: 'LP_NDA' },
                    { label: 'PDF / PowerPoint', tag: 'Export' },
                  ].map((item, i) => (
                    <div key={i} className="flex items-center justify-between p-2 bg-white rounded-lg shadow-sm">
                      <span className="text-sm text-secondary-700">{item.label}</span>
                      <span className={`text-xs px-1.5 py-0.5 rounded ${
                        item.tag === 'IC' ? 'bg-rose-100 text-rose-700' :
                        item.tag === 'LP' ? 'bg-blue-100 text-blue-700' :
                        item.tag === 'LP_NDA' ? 'bg-purple-100 text-purple-700' :
                        'bg-secondary-100 text-secondary-700'
                      }`}>
                        {item.tag}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 詳細セクション */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {/* ソースタグ */}
          <div className="bg-white rounded-2xl shadow-sm ring-1 ring-secondary-900/5 p-6">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">ソースタグ（Source Tag）</h3>
            <p className="text-sm text-secondary-600 mb-4">データの出所を管理</p>
            <div className="space-y-2">
              {[
                { tag: 'PUB', label: '公開情報', desc: 'HP、プレス等', color: 'blue' },
                { tag: 'EXT', label: '外部資料', desc: 'Crunchbase等', color: 'purple' },
                { tag: 'INT', label: 'インタビュー', desc: '経営陣ヒアリング', color: 'amber' },
                { tag: 'CONF', label: '機密情報', desc: 'Term Sheet等', color: 'rose' },
                { tag: 'ANL', label: '内部分析', desc: 'ファンド分析', color: 'emerald' },
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 text-xs font-medium rounded bg-${item.color}-100 text-${item.color}-700`}>
                    {item.tag}
                  </span>
                  <span className="text-sm text-secondary-900">{item.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* 開示レベル */}
          <div className="bg-white rounded-2xl shadow-sm ring-1 ring-secondary-900/5 p-6">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">開示レベル</h3>
            <p className="text-sm text-secondary-600 mb-4">情報の開示範囲を管理</p>
            <div className="space-y-2">
              {[
                { level: 'IC', label: '投資委員会限定', desc: '機密数値含む', color: 'rose' },
                { level: 'LP', label: 'LP開示可', desc: 'レンジ表示', color: 'blue' },
                { level: 'LP_NDA', label: 'LP（NDA付）', desc: '詳細開示', color: 'purple' },
                { level: 'PRIVATE', label: '内部限定', desc: '非開示', color: 'secondary' },
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 text-xs font-medium rounded bg-${item.color}-100 text-${item.color}-700`}>
                    {item.level}
                  </span>
                  <span className="text-sm text-secondary-900">{item.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* レポートセクション */}
          <div className="bg-white rounded-2xl shadow-sm ring-1 ring-secondary-900/5 p-6">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">レポートセクション</h3>
            <p className="text-sm text-secondary-600 mb-4">12セクション構成</p>
            <div className="space-y-1">
              {[
                '投資推奨サマリー',
                '会社概要・課題解決',
                '市場規模・Why Now',
                '競合・差別化',
                '主要KPI',
                '財務ハイライト',
                'チーム',
                'ディール条件',
                'バリュエーション',
                'リスク・対策',
                '価値創造計画',
                '想定Q&A',
              ].map((section, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <span className="text-secondary-400 w-5">{i + 1}.</span>
                  <span className="text-secondary-700">{section}</span>
                </div>
              ))}
            </div>
          </div>

          {/* RBAC */}
          <div className="bg-white rounded-2xl shadow-sm ring-1 ring-secondary-900/5 p-6">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">アクセス制御 (RBAC)</h3>
            <p className="text-sm text-secondary-600 mb-4">4ロールで権限管理</p>
            <div className="space-y-3">
              {[
                { role: 'Analyst', access: 'PUB, EXT, INT(自分)', color: 'blue' },
                { role: 'Lead Partner', access: '上記 + ANL(全)', color: 'purple' },
                { role: 'IC Member', access: '上記 + CONF(全)', color: 'rose' },
                { role: 'Admin', access: 'フルアクセス', color: 'secondary' },
              ].map((item, i) => (
                <div key={i} className="p-2 rounded-lg bg-secondary-50">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`w-2 h-2 rounded-full bg-${item.color}-500`} />
                    <span className="text-sm font-medium text-secondary-900">{item.role}</span>
                  </div>
                  <p className="text-xs text-secondary-500 ml-4">{item.access}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 機能一覧 */}
        <div className="bg-gradient-to-br from-primary-50 to-white rounded-3xl shadow-sm ring-1 ring-primary-100 p-8">
          <h2 className="text-2xl font-bold text-secondary-900 text-center mb-8">主要機能</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: CloudArrowUpIcon,
                title: '資料アップロード',
                features: ['PDF / Excel / スライド対応', 'WebページURL取込', 'ドラッグ&ドロップ', 'バッチ処理'],
              },
              {
                icon: SparklesIcon,
                title: 'AI自動抽出',
                features: ['OCR（画像→テキスト）', 'NLP（構造化抽出）', 'フィールド自動マッピング', '矛盾検出'],
              },
              {
                icon: DocumentChartBarIcon,
                title: 'レポート生成',
                features: ['IC/LP自動切替', 'マスキング自動適用', 'PDF/PPT出力', 'テンプレート管理'],
              },
              {
                icon: CircleStackIcon,
                title: 'データ管理',
                features: ['36+フィールド定義', 'バージョン管理', 'ソース追跡', '監査ログ'],
              },
              {
                icon: ShieldCheckIcon,
                title: 'セキュリティ',
                features: ['RBAC（4ロール）', '開示レベル制御', 'データマスキング', 'アクセスログ'],
              },
              {
                icon: UserGroupIcon,
                title: 'コラボレーション',
                features: ['承認ワークフロー', 'コメント機能', 'タスク管理', '通知'],
              },
            ].map((item, i) => (
              <div key={i} className="bg-white rounded-2xl p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center">
                    <item.icon className="h-5 w-5 text-primary-600" />
                  </div>
                  <h3 className="font-semibold text-secondary-900">{item.title}</h3>
                </div>
                <ul className="space-y-2">
                  {item.features.map((feature, j) => (
                    <li key={j} className="flex items-center gap-2 text-sm text-secondary-600">
                      <CheckCircleIcon className="h-4 w-4 text-emerald-500 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  )
}

