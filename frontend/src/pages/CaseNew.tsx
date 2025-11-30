import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import Layout from '../components/Layout/Layout'
import {
  ArrowLeftIcon,
  BuildingOfficeIcon,
  GlobeAltIcon,
  MapPinIcon,
  TagIcon,
  ChartBarIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline'

export default function CaseNew() {
  const navigate = useNavigate()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    company_name: '',
    stage: 'early',
    website_url: '',
    industry: '',
    location: '',
    description: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    // デモ用: 擬似的な遅延
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 実際のAPIコール（デモではスキップ）
    // await api.post('/cases', formData)

    setIsSubmitting(false)
    navigate('/cases')
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto px-4 sm:px-0">
        {/* Header */}
        <div className="mb-10">
          <Link
            to="/cases"
            className="group inline-flex items-center gap-2 text-sm text-secondary-500 hover:text-primary-600 transition-colors mb-6"
          >
            <ArrowLeftIcon className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
            案件一覧に戻る
          </Link>
          <h1 className="text-3xl font-bold tracking-tight text-secondary-900">
            新規案件の作成
          </h1>
          <p className="mt-3 text-base text-secondary-500">
            投資検討対象の企業情報を入力してください。<span className="text-danger">*</span> は必須項目です。
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-10">
          {/* 基本情報セクション */}
          <div className="bg-white shadow-sm ring-1 ring-secondary-200/60 rounded-2xl overflow-hidden">
            <div className="border-b border-secondary-200 bg-secondary-50/50 px-8 py-5">
              <h2 className="text-lg font-semibold text-secondary-900 flex items-center gap-3">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-100 text-primary-600">
                  <BuildingOfficeIcon className="h-5 w-5" />
                </span>
                基本情報
              </h2>
            </div>

            <div className="px-8 py-8 space-y-8">
              {/* 会社名 */}
              <div>
                <label htmlFor="company_name" className="block text-sm font-semibold text-secondary-900 mb-2">
                  会社名 <span className="text-danger">*</span>
                </label>
                <div className="relative">
                  <input
                    type="text"
                    name="company_name"
                    id="company_name"
                    required
                    value={formData.company_name}
                    onChange={handleChange}
                    className="block w-full rounded-xl border-0 px-4 py-3.5 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 placeholder:text-secondary-400 focus:ring-2 focus:ring-inset focus:ring-primary-500 transition-shadow text-base"
                    placeholder="株式会社テックスタートアップ"
                  />
                </div>
                <p className="mt-2 text-sm text-secondary-500">
                  正式な会社名を入力してください
                </p>
              </div>

              {/* 2カラムレイアウト */}
              <div className="grid grid-cols-1 gap-8 sm:grid-cols-2">
                {/* 投資ステージ */}
                <div>
                  <label htmlFor="stage" className="block text-sm font-semibold text-secondary-900 mb-2">
                    投資ステージ <span className="text-danger">*</span>
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <ChartBarIcon className="h-5 w-5 text-secondary-400" />
                    </div>
                    <select
                      name="stage"
                      id="stage"
                      required
                      value={formData.stage}
                      onChange={handleChange}
                      className="block w-full rounded-xl border-0 pl-11 pr-10 py-3.5 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 focus:ring-2 focus:ring-inset focus:ring-primary-500 transition-shadow text-base appearance-none bg-white"
                    >
                      <option value="seed">Seed（シード）</option>
                      <option value="early">Early（アーリー）</option>
                      <option value="growth">Growth（グロース）</option>
                      <option value="late">Late（レイト）</option>
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
                      <svg className="h-5 w-5 text-secondary-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
                      </svg>
                    </div>
                  </div>
                  <p className="mt-2 text-sm text-secondary-500">
                    現在の投資検討フェーズを選択
                  </p>
                </div>

                {/* 業界 */}
                <div>
                  <label htmlFor="industry" className="block text-sm font-semibold text-secondary-900 mb-2">
                    業界・セクター
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <TagIcon className="h-5 w-5 text-secondary-400" />
                    </div>
                    <input
                      type="text"
                      name="industry"
                      id="industry"
                      value={formData.industry}
                      onChange={handleChange}
                      className="block w-full rounded-xl border-0 pl-11 pr-4 py-3.5 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 placeholder:text-secondary-400 focus:ring-2 focus:ring-inset focus:ring-primary-500 transition-shadow text-base"
                      placeholder="SaaS / FinTech / HealthTech"
                    />
                  </div>
                  <p className="mt-2 text-sm text-secondary-500">
                    複数の場合はスラッシュで区切ってください
                  </p>
                </div>
              </div>

              {/* 2カラムレイアウト */}
              <div className="grid grid-cols-1 gap-8 sm:grid-cols-2">
                {/* WebサイトURL */}
                <div>
                  <label htmlFor="website_url" className="block text-sm font-semibold text-secondary-900 mb-2">
                    Webサイト
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <GlobeAltIcon className="h-5 w-5 text-secondary-400" />
                    </div>
                    <input
                      type="url"
                      name="website_url"
                      id="website_url"
                      value={formData.website_url}
                      onChange={handleChange}
                      className="block w-full rounded-xl border-0 pl-11 pr-4 py-3.5 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 placeholder:text-secondary-400 focus:ring-2 focus:ring-inset focus:ring-primary-500 transition-shadow text-base"
                      placeholder="https://example.com"
                    />
                  </div>
                  <p className="mt-2 text-sm text-secondary-500">
                    企業の公式サイトURL
                  </p>
                </div>

                {/* 所在地 */}
                <div>
                  <label htmlFor="location" className="block text-sm font-semibold text-secondary-900 mb-2">
                    所在地
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <MapPinIcon className="h-5 w-5 text-secondary-400" />
                    </div>
                    <input
                      type="text"
                      name="location"
                      id="location"
                      value={formData.location}
                      onChange={handleChange}
                      className="block w-full rounded-xl border-0 pl-11 pr-4 py-3.5 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 placeholder:text-secondary-400 focus:ring-2 focus:ring-inset focus:ring-primary-500 transition-shadow text-base"
                      placeholder="東京都渋谷区"
                    />
                  </div>
                  <p className="mt-2 text-sm text-secondary-500">
                    本社または主要拠点の所在地
                  </p>
                </div>
              </div>

              {/* 事業概要 */}
              <div>
                <label htmlFor="description" className="block text-sm font-semibold text-secondary-900 mb-2">
                  事業概要
                </label>
                <div className="relative">
                  <div className="absolute top-4 left-4 pointer-events-none">
                    <DocumentTextIcon className="h-5 w-5 text-secondary-400" />
                  </div>
                  <textarea
                    name="description"
                    id="description"
                    rows={5}
                    value={formData.description}
                    onChange={handleChange}
                    className="block w-full rounded-xl border-0 pl-11 pr-4 py-3.5 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 placeholder:text-secondary-400 focus:ring-2 focus:ring-inset focus:ring-primary-500 transition-shadow text-base resize-none"
                    placeholder="企業の事業内容、提供サービス、ターゲット市場、競合優位性などを記載してください。"
                  />
                </div>
                <p className="mt-2 text-sm text-secondary-500">
                  投資判断に必要な情報を簡潔にまとめてください（500文字程度推奨）
                </p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 pb-8">
            <Link
              to="/cases"
              className="inline-flex items-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold text-secondary-700 hover:text-secondary-900 hover:bg-secondary-100 transition-colors"
            >
              キャンセル
            </Link>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary-600 px-8 py-3.5 text-base font-semibold text-white shadow-lg shadow-primary-500/25 hover:bg-primary-500 hover:shadow-xl hover:shadow-primary-500/30 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none transition-all duration-200"
            >
              {isSubmitting ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  作成中...
                </>
              ) : (
                '案件を作成'
              )}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  )
}
