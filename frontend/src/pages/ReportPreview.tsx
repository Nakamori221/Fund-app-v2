// A: ICレポートプレビューページ - 最終出力フォーマットのサンプル表示
import { useState } from 'react'
import Layout from '../components/Layout/Layout'
import {
  DocumentTextIcon,
  ChartBarIcon,
  UserGroupIcon,
  CurrencyDollarIcon,
  ShieldExclamationIcon,
  LightBulbIcon,
  BuildingOfficeIcon,
  GlobeAltIcon,
  ArrowDownTrayIcon,
  EyeIcon,
  DocumentDuplicateIcon,
} from '@heroicons/react/24/outline'

// レポートセクションの型定義
interface ReportSection {
  id: string
  title: string
  icon: React.ComponentType<{ className?: string }>
  content: React.ReactNode
  visibleInLP: boolean
}

export default function ReportPreview() {
  const [reportType, setReportType] = useState<'ic' | 'lp'>('ic')
  const [selectedCase] = useState({
    company_name: 'TechCorp Inc.',
    stage: 'Early',
    industry: 'SaaS / Enterprise',
  })

  // レポートセクション定義
  const sections: ReportSection[] = [
    {
      id: 'exec_summary',
      title: '投資推奨サマリー',
      icon: LightBulbIcon,
      visibleInLP: true,
      content: (
        <div className="space-y-4">
          <div className="bg-primary-50 border-l-4 border-primary-500 p-4 rounded-r-lg">
            <h4 className="font-semibold text-primary-900 mb-2">投資テーゼ</h4>
            <p className="text-secondary-700">
              TechCorp Inc.は、エンタープライズ向けAI分析プラットフォームを提供するB2B SaaS企業。
              高いNDR（130%）と急成長するARR（前年比180%成長）により、シリーズBでの投資推奨。
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white border border-secondary-200 rounded-xl p-4">
              <p className="text-xs text-secondary-500 mb-1">投資額</p>
              <p className="text-xl font-bold text-secondary-900">
                {reportType === 'ic' ? '$5.0M' : '$5-7M'}
              </p>
            </div>
            <div className="bg-white border border-secondary-200 rounded-xl p-4">
              <p className="text-xs text-secondary-500 mb-1">持分比率</p>
              <p className="text-xl font-bold text-secondary-900">
                {reportType === 'ic' ? '12.5%' : '10-15%'}
              </p>
            </div>
            <div className="bg-white border border-secondary-200 rounded-xl p-4">
              <p className="text-xs text-secondary-500 mb-1">Pre-Money評価額</p>
              <p className="text-xl font-bold text-secondary-900">
                {reportType === 'ic' ? '$40M' : '$35-45M'}
              </p>
            </div>
          </div>
          <div className="space-y-2">
            <h4 className="font-semibold text-secondary-900">投資理由</h4>
            <ol className="list-decimal list-inside space-y-1 text-secondary-700">
              <li>市場リーダーシップ：エンタープライズAI分析市場で急成長中</li>
              <li>強固なユニットエコノミクス：LTV/CAC比率 5.2x、ペイバック12ヶ月</li>
              <li>優秀な経営陣：元Google/Salesforceの経験豊富なチーム</li>
            </ol>
          </div>
        </div>
      ),
    },
    {
      id: 'company_overview',
      title: '会社概要・課題解決',
      icon: BuildingOfficeIcon,
      visibleInLP: true,
      content: (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-secondary-900 mb-2">課題</h4>
              <p className="text-secondary-700">
                エンタープライズ企業は大量のデータを保有しているが、その分析・活用に
                専門知識と時間が必要。既存のBIツールは設定が複雑で、ビジネスユーザーが
                自律的に分析を行うことが困難。
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-secondary-900 mb-2">ソリューション</h4>
              <p className="text-secondary-700">
                AIを活用した自然言語クエリにより、非技術者でも高度なデータ分析が可能。
                既存のデータウェアハウスと連携し、導入から価値実現までの時間を大幅に短縮。
              </p>
            </div>
          </div>
          <div>
            <h4 className="font-semibold text-secondary-900 mb-2">ビジネスモデル</h4>
            <p className="text-secondary-700">
              SaaSサブスクリプションモデル。席数ベースの料金体系（$50-200/user/月）。
              エンタープライズ契約は年間契約が中心（ACV $50K-500K）。
            </p>
          </div>
        </div>
      ),
    },
    {
      id: 'market_analysis',
      title: '市場規模・Why Now',
      icon: GlobeAltIcon,
      visibleInLP: true,
      content: (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gradient-to-br from-primary-50 to-white rounded-xl border border-primary-100">
              <p className="text-xs text-secondary-500 mb-1">TAM</p>
              <p className="text-2xl font-bold text-primary-600">$45B</p>
              <p className="text-xs text-secondary-500">Global BI Market</p>
            </div>
            <div className="text-center p-4 bg-gradient-to-br from-primary-50 to-white rounded-xl border border-primary-100">
              <p className="text-xs text-secondary-500 mb-1">SAM</p>
              <p className="text-2xl font-bold text-primary-600">$12B</p>
              <p className="text-xs text-secondary-500">Enterprise AI Analytics</p>
            </div>
            <div className="text-center p-4 bg-gradient-to-br from-primary-50 to-white rounded-xl border border-primary-100">
              <p className="text-xs text-secondary-500 mb-1">SOM</p>
              <p className="text-2xl font-bold text-primary-600">$800M</p>
              <p className="text-xs text-secondary-500">Initial Target</p>
            </div>
          </div>
          <div>
            <h4 className="font-semibold text-secondary-900 mb-2">Why Now</h4>
            <ul className="list-disc list-inside space-y-1 text-secondary-700">
              <li>生成AI技術の成熟により、自然言語でのデータクエリが実用レベルに</li>
              <li>エンタープライズのデータ量増加（年率40%成長）</li>
              <li>データドリブン経営の必要性に対する認識の高まり</li>
            </ul>
          </div>
        </div>
      ),
    },
    {
      id: 'kpi_overview',
      title: '主要KPI・ユニットエコノミクス',
      icon: ChartBarIcon,
      visibleInLP: true,
      content: (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-secondary-200 rounded-xl p-4">
              <p className="text-xs text-secondary-500 mb-1">ARR</p>
              <p className="text-xl font-bold text-secondary-900">$3.2M</p>
              <p className="text-xs text-emerald-600">+180% YoY</p>
            </div>
            <div className="bg-white border border-secondary-200 rounded-xl p-4">
              <p className="text-xs text-secondary-500 mb-1">MRR</p>
              <p className="text-xl font-bold text-secondary-900">$267K</p>
              <p className="text-xs text-emerald-600">+15% MoM</p>
            </div>
            <div className="bg-white border border-secondary-200 rounded-xl p-4">
              <p className="text-xs text-secondary-500 mb-1">NDR</p>
              <p className="text-xl font-bold text-secondary-900">130%</p>
              <p className="text-xs text-secondary-500">Annual</p>
            </div>
            <div className="bg-white border border-secondary-200 rounded-xl p-4">
              <p className="text-xs text-secondary-500 mb-1">Logo Churn</p>
              <p className="text-xl font-bold text-secondary-900">2.1%</p>
              <p className="text-xs text-secondary-500">Monthly</p>
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
              <p className="text-xs text-emerald-600 mb-1">LTV/CAC</p>
              <p className="text-xl font-bold text-emerald-700">5.2x</p>
            </div>
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
              <p className="text-xs text-emerald-600 mb-1">Payback Period</p>
              <p className="text-xl font-bold text-emerald-700">12 mo</p>
            </div>
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
              <p className="text-xs text-emerald-600 mb-1">Gross Margin</p>
              <p className="text-xl font-bold text-emerald-700">78%</p>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'financials',
      title: '財務ハイライト',
      icon: CurrencyDollarIcon,
      visibleInLP: false, // IC only
      content: (
        <div className="space-y-4">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-secondary-200">
              <thead>
                <tr className="bg-secondary-50">
                  <th className="px-4 py-3 text-left text-xs font-medium text-secondary-500 uppercase">項目</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-secondary-500 uppercase">2023実績</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-secondary-500 uppercase">2024予測</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-secondary-500 uppercase">2025予測</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-secondary-200">
                <tr>
                  <td className="px-4 py-3 text-sm text-secondary-900">ARR</td>
                  <td className="px-4 py-3 text-sm text-right text-secondary-700">$1.2M</td>
                  <td className="px-4 py-3 text-sm text-right text-secondary-700">$3.2M</td>
                  <td className="px-4 py-3 text-sm text-right text-secondary-700">$8.0M</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 text-sm text-secondary-900">売上総利益</td>
                  <td className="px-4 py-3 text-sm text-right text-secondary-700">$0.9M</td>
                  <td className="px-4 py-3 text-sm text-right text-secondary-700">$2.5M</td>
                  <td className="px-4 py-3 text-sm text-right text-secondary-700">$6.2M</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 text-sm text-secondary-900">営業費用</td>
                  <td className="px-4 py-3 text-sm text-right text-secondary-700">$2.1M</td>
                  <td className="px-4 py-3 text-sm text-right text-secondary-700">$4.5M</td>
                  <td className="px-4 py-3 text-sm text-right text-secondary-700">$7.0M</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 text-sm text-secondary-900">営業利益</td>
                  <td className="px-4 py-3 text-sm text-right text-rose-600">-$1.2M</td>
                  <td className="px-4 py-3 text-sm text-right text-rose-600">-$2.0M</td>
                  <td className="px-4 py-3 text-sm text-right text-rose-600">-$0.8M</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
            <h4 className="font-semibold text-amber-900 mb-2">主要仮定</h4>
            <ul className="text-sm text-amber-800 space-y-1">
              <li>• ARR成長率: 150%（2024→2025）</li>
              <li>• 粗利率: 78%を維持</li>
              <li>• S&M費用: ARRの60%（効率化により50%へ改善見込み）</li>
            </ul>
          </div>
        </div>
      ),
    },
    {
      id: 'team',
      title: 'チーム・組織体制',
      icon: UserGroupIcon,
      visibleInLP: true,
      content: (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { name: '山田 太郎', role: 'CEO', bg: '元Google Japan部長、15年のエンタープライズ経験' },
              { name: '佐藤 花子', role: 'CTO', bg: '元Salesforce Principal Engineer、AI/ML専門' },
              { name: 'John Smith', role: 'CRO', bg: '元Tableau VP Sales、エンタープライズ営業20年' },
            ].map((member, i) => (
              <div key={i} className="bg-white border border-secondary-200 rounded-xl p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold">
                    {member.name.charAt(0)}
                  </div>
                  <div>
                    <p className="font-semibold text-secondary-900">{member.name}</p>
                    <p className="text-xs text-primary-600">{member.role}</p>
                  </div>
                </div>
                <p className="text-xs text-secondary-600">{member.bg}</p>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-secondary-50 rounded-xl p-4">
              <p className="text-xs text-secondary-500 mb-1">従業員数</p>
              <p className="text-xl font-bold text-secondary-900">45名</p>
              <p className="text-xs text-secondary-500">エンジニア25名、営業12名、その他8名</p>
            </div>
            <div className="bg-secondary-50 rounded-xl p-4">
              <p className="text-xs text-secondary-500 mb-1">採用計画</p>
              <p className="text-xl font-bold text-secondary-900">+30名</p>
              <p className="text-xs text-secondary-500">2024年末目標: 75名</p>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'risk_mitigation',
      title: 'リスク・対策',
      icon: ShieldExclamationIcon,
      visibleInLP: true,
      content: (
        <div className="space-y-3">
          {[
            { risk: '競合（大手BI企業のAI機能追加）', impact: '高', mitigation: '独自AI技術の特許取得、深いインテグレーション' },
            { risk: '景気後退による企業IT投資削減', impact: '中', mitigation: 'ROI実証済み顧客事例の蓄積、コスト削減訴求' },
            { risk: 'キーパーソン離職リスク', impact: '中', mitigation: 'ストックオプション設計、採用パイプライン強化' },
          ].map((item, i) => (
            <div key={i} className="bg-white border border-secondary-200 rounded-xl p-4">
              <div className="flex items-start justify-between mb-2">
                <p className="font-medium text-secondary-900">{item.risk}</p>
                <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                  item.impact === '高' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'
                }`}>
                  影響度: {item.impact}
                </span>
              </div>
              <p className="text-sm text-secondary-600">
                <span className="font-medium text-emerald-600">対策:</span> {item.mitigation}
              </p>
            </div>
          ))}
        </div>
      ),
    },
  ]

  // 表示するセクションをフィルタリング
  const visibleSections = reportType === 'ic' 
    ? sections 
    : sections.filter(s => s.visibleInLP)

  return (
    <Layout>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* ヘッダー */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-secondary-900">ICレポート プレビュー</h1>
              <p className="mt-2 text-secondary-500">最終出力フォーマットのサンプル表示</p>
            </div>
            <div className="flex items-center gap-3">
              <button className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-secondary-700 bg-white rounded-lg border border-secondary-300 hover:bg-secondary-50">
                <DocumentDuplicateIcon className="h-4 w-4" />
                複製
              </button>
              <button className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700">
                <ArrowDownTrayIcon className="h-4 w-4" />
                エクスポート
              </button>
            </div>
          </div>

          {/* レポートタイプ切り替え */}
          <div className="flex items-center gap-4 p-1 bg-secondary-100 rounded-xl w-fit">
            <button
              onClick={() => setReportType('ic')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                reportType === 'ic'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-secondary-600 hover:text-secondary-900'
              }`}
            >
              <EyeIcon className="h-4 w-4 inline mr-2" />
              IC資料（フル版）
            </button>
            <button
              onClick={() => setReportType('lp')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                reportType === 'lp'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-secondary-600 hover:text-secondary-900'
              }`}
            >
              <EyeIcon className="h-4 w-4 inline mr-2" />
              LP資料（マスク版）
            </button>
          </div>
        </div>

        {/* レポートヘッダー */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-6 mb-6 text-white">
          <div className="flex items-center gap-2 text-primary-200 text-sm mb-2">
            <DocumentTextIcon className="h-4 w-4" />
            <span>{reportType === 'ic' ? '投資委員会資料' : 'LP向け開示資料'}</span>
          </div>
          <h2 className="text-2xl font-bold mb-1">{selectedCase.company_name}</h2>
          <div className="flex items-center gap-4 text-primary-100 text-sm">
            <span>{selectedCase.stage} Stage</span>
            <span>•</span>
            <span>{selectedCase.industry}</span>
            <span>•</span>
            <span>作成日: 2025年11月30日</span>
          </div>
        </div>

        {/* 目次 */}
        <div className="bg-white rounded-2xl shadow-lg ring-1 ring-secondary-900/5 p-4 mb-6">
          <h3 className="text-sm font-medium text-secondary-500 mb-3">目次</h3>
          <div className="flex flex-wrap gap-2">
            {visibleSections.map((section, index) => (
              <a
                key={section.id}
                href={`#${section.id}`}
                className="px-3 py-1.5 text-sm text-secondary-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              >
                {index + 1}. {section.title}
              </a>
            ))}
          </div>
        </div>

        {/* レポートセクション */}
        <div className="space-y-6">
          {visibleSections.map((section, index) => {
            const Icon = section.icon
            return (
              <div
                key={section.id}
                id={section.id}
                className="bg-white rounded-2xl shadow-lg ring-1 ring-secondary-900/5 overflow-hidden"
              >
                <div className="bg-secondary-50 px-6 py-4 border-b border-secondary-200">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-primary-100 flex items-center justify-center">
                      <Icon className="h-4 w-4 text-primary-600" />
                    </div>
                    <div>
                      <span className="text-xs text-secondary-500">セクション {index + 1}</span>
                      <h3 className="text-lg font-semibold text-secondary-900">{section.title}</h3>
                    </div>
                  </div>
                </div>
                <div className="p-6">
                  {section.content}
                </div>
              </div>
            )
          })}
        </div>

        {/* フッター */}
        <div className="mt-8 pt-6 border-t border-secondary-200 text-center text-sm text-secondary-500">
          <p>本資料は投資判断の参考資料であり、投資勧誘を目的としたものではありません。</p>
          <p className="mt-1">Confidential - {reportType === 'ic' ? '投資委員会限定' : 'LP向け開示可'}</p>
        </div>
      </div>
    </Layout>
  )
}

