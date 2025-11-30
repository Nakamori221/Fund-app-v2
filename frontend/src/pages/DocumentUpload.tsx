// B: 資料アップロードページ - Phase 1 入力UI
import { useState, useCallback } from 'react'
import Layout from '../components/Layout/Layout'
import {
  CloudArrowUpIcon,
  DocumentTextIcon,
  GlobeAltIcon,
  TableCellsIcon,
  FolderIcon,
  CheckCircleIcon,
  XMarkIcon,
  ArrowPathIcon,
  DocumentMagnifyingGlassIcon,
  SparklesIcon,
  LinkIcon,
  DocumentArrowUpIcon,
} from '@heroicons/react/24/outline'

// アップロードされたファイルの型
interface UploadedFile {
  id: string
  name: string
  type: 'pdf' | 'excel' | 'slide' | 'url' | 'other'
  size?: string
  url?: string
  status: 'uploading' | 'processing' | 'completed' | 'error'
  extractedFields?: number
  progress?: number
}

// ファイルタイプのアイコンを取得
function getFileIcon(type: UploadedFile['type']) {
  switch (type) {
    case 'pdf':
      return DocumentTextIcon
    case 'excel':
      return TableCellsIcon
    case 'slide':
      return FolderIcon
    case 'url':
      return GlobeAltIcon
    default:
      return DocumentTextIcon
  }
}

// ファイルタイプのラベルを取得
function getFileTypeLabel(type: UploadedFile['type']) {
  switch (type) {
    case 'pdf':
      return 'PDF'
    case 'excel':
      return 'Excel/CSV'
    case 'slide':
      return 'スライド'
    case 'url':
      return 'Webページ'
    default:
      return 'その他'
  }
}

export default function DocumentUpload() {
  const [urlInput, setUrlInput] = useState('')
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([
    // デモ用のサンプルデータ
    {
      id: '1',
      name: 'TechCorp_会社概要.pdf',
      type: 'pdf',
      size: '2.4 MB',
      status: 'completed',
      extractedFields: 12,
    },
    {
      id: '2',
      name: '売上実績_2024Q3.xlsx',
      type: 'excel',
      size: '156 KB',
      status: 'completed',
      extractedFields: 8,
    },
    {
      id: '3',
      name: 'ピッチデッキ_SeriesB.pptx',
      type: 'slide',
      size: '5.8 MB',
      status: 'processing',
      progress: 65,
    },
  ])
  const [isDragging, setIsDragging] = useState(false)

  // ファイルドロップハンドラー
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files)
    handleFiles(files)
  }, [])

  // ファイル選択ハンドラー
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    handleFiles(files)
  }

  // ファイル処理
  const handleFiles = (files: File[]) => {
    const newFiles: UploadedFile[] = files.map(file => {
      let type: UploadedFile['type'] = 'other'
      if (file.name.endsWith('.pdf')) type = 'pdf'
      else if (file.name.endsWith('.xlsx') || file.name.endsWith('.csv')) type = 'excel'
      else if (file.name.endsWith('.pptx') || file.name.endsWith('.ppt')) type = 'slide'

      return {
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        type,
        size: `${(file.size / 1024 / 1024).toFixed(1)} MB`,
        status: 'uploading',
        progress: 0,
      }
    })

    setUploadedFiles(prev => [...newFiles, ...prev])

    // デモ用：アップロードと処理をシミュレート
    newFiles.forEach(file => {
      simulateUpload(file.id)
    })
  }

  // URL追加ハンドラー
  const handleAddUrl = () => {
    if (!urlInput.trim()) return

    const newFile: UploadedFile = {
      id: Math.random().toString(36).substr(2, 9),
      name: urlInput,
      type: 'url',
      url: urlInput,
      status: 'processing',
      progress: 30,
    }

    setUploadedFiles(prev => [newFile, ...prev])
    setUrlInput('')
    simulateUpload(newFile.id)
  }

  // アップロードシミュレーション
  const simulateUpload = (fileId: string) => {
    let progress = 0
    const interval = setInterval(() => {
      progress += Math.random() * 30
      if (progress >= 100) {
        progress = 100
        clearInterval(interval)
        setUploadedFiles(prev =>
          prev.map(f =>
            f.id === fileId
              ? { ...f, status: 'completed', extractedFields: Math.floor(Math.random() * 15) + 5, progress: 100 }
              : f
          )
        )
      } else {
        setUploadedFiles(prev =>
          prev.map(f =>
            f.id === fileId ? { ...f, progress: Math.min(progress, 99), status: 'processing' } : f
          )
        )
      }
    }, 500)
  }

  // ファイル削除
  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId))
  }

  // 完了したファイル数
  const completedCount = uploadedFiles.filter(f => f.status === 'completed').length
  const totalExtracted = uploadedFiles
    .filter(f => f.status === 'completed')
    .reduce((sum, f) => sum + (f.extractedFields || 0), 0)

  return (
    <Layout>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* ヘッダー */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-secondary-900">資料アップロード</h1>
          <p className="mt-2 text-secondary-500">
            既存資料からデータを抽出し、ICレポートに自動入力します
          </p>
        </div>

        {/* 統計カード */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-2xl shadow-sm ring-1 ring-secondary-900/5 p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center">
                <DocumentArrowUpIcon className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-secondary-900">{uploadedFiles.length}</p>
                <p className="text-sm text-secondary-500">アップロード済み</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-2xl shadow-sm ring-1 ring-secondary-900/5 p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
                <CheckCircleIcon className="h-5 w-5 text-emerald-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-secondary-900">{completedCount}</p>
                <p className="text-sm text-secondary-500">処理完了</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-2xl shadow-sm ring-1 ring-secondary-900/5 p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center">
                <SparklesIcon className="h-5 w-5 text-amber-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-secondary-900">{totalExtracted}</p>
                <p className="text-sm text-secondary-500">抽出フィールド</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左側：アップロードエリア */}
          <div className="lg:col-span-2 space-y-6">
            {/* ドラッグ&ドロップエリア */}
            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              className={`
                relative border-2 border-dashed rounded-2xl p-8 text-center transition-all
                ${isDragging
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-secondary-300 hover:border-primary-400 hover:bg-secondary-50'
                }
              `}
            >
              <input
                type="file"
                multiple
                accept=".pdf,.xlsx,.xls,.csv,.pptx,.ppt,.doc,.docx"
                onChange={handleFileSelect}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <CloudArrowUpIcon className={`h-12 w-12 mx-auto mb-4 ${isDragging ? 'text-primary-500' : 'text-secondary-400'}`} />
              <p className="text-lg font-medium text-secondary-900 mb-2">
                ファイルをドラッグ&ドロップ
              </p>
              <p className="text-sm text-secondary-500 mb-4">
                または <span className="text-primary-600 font-medium">クリックして選択</span>
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {['PDF', 'Excel/CSV', 'PowerPoint', 'Word'].map(type => (
                  <span key={type} className="px-2 py-1 text-xs bg-secondary-100 text-secondary-600 rounded-lg">
                    {type}
                  </span>
                ))}
              </div>
            </div>

            {/* URL入力 */}
            <div className="bg-white rounded-2xl shadow-sm ring-1 ring-secondary-900/5 p-5">
              <h3 className="font-medium text-secondary-900 mb-3 flex items-center gap-2">
                <LinkIcon className="h-5 w-5 text-secondary-400" />
                WebページURLを追加
              </h3>
              <div className="flex gap-3">
                <input
                  type="url"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://example.com/company-page"
                  className="flex-1 rounded-xl border-0 py-3 px-4 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 placeholder:text-secondary-400 focus:ring-2 focus:ring-inset focus:ring-primary-500"
                />
                <button
                  onClick={handleAddUrl}
                  disabled={!urlInput.trim()}
                  className="px-5 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  追加
                </button>
              </div>
              <p className="mt-2 text-xs text-secondary-500">
                HP、ランディングページ、プレスリリースなどのURLを入力
              </p>
            </div>

            {/* アップロードファイル一覧 */}
            <div className="bg-white rounded-2xl shadow-sm ring-1 ring-secondary-900/5 overflow-hidden">
              <div className="px-5 py-4 border-b border-secondary-200">
                <h3 className="font-medium text-secondary-900">アップロードファイル</h3>
              </div>
              <div className="divide-y divide-secondary-100">
                {uploadedFiles.length === 0 ? (
                  <div className="p-8 text-center text-secondary-500">
                    <FolderIcon className="h-12 w-12 mx-auto mb-3 text-secondary-300" />
                    <p>まだファイルがアップロードされていません</p>
                  </div>
                ) : (
                  uploadedFiles.map(file => {
                    const Icon = getFileIcon(file.type)
                    return (
                      <div key={file.id} className="p-4 hover:bg-secondary-50 transition-colors">
                        <div className="flex items-center gap-4">
                          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                            file.type === 'pdf' ? 'bg-rose-100 text-rose-600' :
                            file.type === 'excel' ? 'bg-emerald-100 text-emerald-600' :
                            file.type === 'slide' ? 'bg-amber-100 text-amber-600' :
                            file.type === 'url' ? 'bg-blue-100 text-blue-600' :
                            'bg-secondary-100 text-secondary-600'
                          }`}>
                            <Icon className="h-5 w-5" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-secondary-900 truncate">{file.name}</p>
                            <div className="flex items-center gap-2 text-xs text-secondary-500">
                              <span>{getFileTypeLabel(file.type)}</span>
                              {file.size && (
                                <>
                                  <span>•</span>
                                  <span>{file.size}</span>
                                </>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            {file.status === 'uploading' && (
                              <div className="flex items-center gap-2 text-secondary-500">
                                <ArrowPathIcon className="h-4 w-4 animate-spin" />
                                <span className="text-sm">アップロード中...</span>
                              </div>
                            )}
                            {file.status === 'processing' && (
                              <div className="w-24">
                                <div className="flex items-center gap-2 mb-1">
                                  <DocumentMagnifyingGlassIcon className="h-4 w-4 text-primary-500" />
                                  <span className="text-xs text-primary-600">解析中</span>
                                </div>
                                <div className="h-1.5 bg-secondary-200 rounded-full overflow-hidden">
                                  <div 
                                    className="h-full bg-primary-500 rounded-full transition-all"
                                    style={{ width: `${file.progress}%` }}
                                  />
                                </div>
                              </div>
                            )}
                            {file.status === 'completed' && (
                              <div className="flex items-center gap-2 text-emerald-600">
                                <CheckCircleIcon className="h-5 w-5" />
                                <span className="text-sm font-medium">{file.extractedFields}項目</span>
                              </div>
                            )}
                            {file.status === 'error' && (
                              <span className="text-sm text-rose-600">エラー</span>
                            )}
                            <button
                              onClick={() => removeFile(file.id)}
                              className="p-1.5 text-secondary-400 hover:text-secondary-600 hover:bg-secondary-100 rounded-lg transition-colors"
                            >
                              <XMarkIcon className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    )
                  })
                )}
              </div>
            </div>
          </div>

          {/* 右側：ガイド */}
          <div className="space-y-6">
            {/* 対応ソースタイプ */}
            <div className="bg-white rounded-2xl shadow-sm ring-1 ring-secondary-900/5 p-5">
              <h3 className="font-medium text-secondary-900 mb-4">対応ソースタイプ</h3>
              <div className="space-y-3">
                {[
                  { icon: GlobeAltIcon, label: 'Webページ', desc: 'HP、LP、プレスリリース', color: 'blue' },
                  { icon: DocumentTextIcon, label: 'PDF文書', desc: '会社概要、IR資料', color: 'rose' },
                  { icon: TableCellsIcon, label: 'Excel/CSV', desc: '売上データ、KPI一覧', color: 'emerald' },
                  { icon: FolderIcon, label: 'スライド', desc: 'ピッチデッキ、提案書', color: 'amber' },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-secondary-50">
                    <div className={`w-8 h-8 rounded-lg bg-${item.color}-100 flex items-center justify-center`}>
                      <item.icon className={`h-4 w-4 text-${item.color}-600`} />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-secondary-900">{item.label}</p>
                      <p className="text-xs text-secondary-500">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI抽出の仕組み */}
            <div className="bg-gradient-to-br from-primary-50 to-white rounded-2xl shadow-sm ring-1 ring-primary-100 p-5">
              <div className="flex items-center gap-2 mb-3">
                <SparklesIcon className="h-5 w-5 text-primary-600" />
                <h3 className="font-medium text-primary-900">AI自動抽出</h3>
              </div>
              <ul className="space-y-2 text-sm text-secondary-700">
                <li className="flex items-start gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-primary-500 mt-0.5 flex-shrink-0" />
                  <span>会社概要・事業内容を自動認識</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-primary-500 mt-0.5 flex-shrink-0" />
                  <span>財務数値（売上、利益等）を抽出</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-primary-500 mt-0.5 flex-shrink-0" />
                  <span>KPI指標を構造化データに変換</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-primary-500 mt-0.5 flex-shrink-0" />
                  <span>レポートフォーマットに自動マッピング</span>
                </li>
              </ul>
            </div>

            {/* 次のステップ */}
            <div className="bg-white rounded-2xl shadow-sm ring-1 ring-secondary-900/5 p-5">
              <h3 className="font-medium text-secondary-900 mb-3">処理フロー</h3>
              <div className="space-y-3">
                {[
                  { step: '1', label: 'アップロード', done: true },
                  { step: '2', label: 'AI解析・抽出', done: completedCount > 0 },
                  { step: '3', label: 'データ確認・修正', done: false },
                  { step: '4', label: 'レポート生成', done: false },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                      item.done 
                        ? 'bg-emerald-100 text-emerald-700' 
                        : 'bg-secondary-100 text-secondary-500'
                    }`}>
                      {item.done ? <CheckCircleIcon className="h-4 w-4" /> : item.step}
                    </div>
                    <span className={`text-sm ${item.done ? 'text-secondary-900' : 'text-secondary-500'}`}>
                      {item.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

