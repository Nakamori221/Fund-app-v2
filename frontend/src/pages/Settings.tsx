import { useState } from 'react'
import Layout from '../components/Layout/Layout'
import { useAuthStore } from '../stores/authStore'
import {
  UserCircleIcon,
  BellIcon,
  ShieldCheckIcon,
  Cog6ToothIcon,
  CameraIcon,
} from '@heroicons/react/24/outline'

const tabs = [
  { id: 'profile', name: 'プロフィール', icon: UserCircleIcon },
  { id: 'notifications', name: '通知設定', icon: BellIcon },
  { id: 'security', name: 'セキュリティ', icon: ShieldCheckIcon },
  { id: 'preferences', name: '環境設定', icon: Cog6ToothIcon },
]

export default function Settings() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('profile')
  const [isSaving, setIsSaving] = useState(false)

  const handleSave = async () => {
    setIsSaving(true)
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsSaving(false)
  }

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-secondary-900">
            設定
          </h1>
          <p className="mt-3 text-base text-secondary-500">
            アカウントとアプリケーションの設定を管理します
          </p>
        </div>

        <div className="lg:grid lg:grid-cols-12 lg:gap-x-10">
          {/* Sidebar */}
          <aside className="lg:col-span-3">
            <nav className="flex flex-row lg:flex-col gap-2 overflow-x-auto pb-4 lg:pb-0">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-3 px-4 py-3.5 text-sm font-semibold rounded-xl whitespace-nowrap transition-all duration-200
                    ${activeTab === tab.id
                      ? 'bg-primary-50 text-primary-700 shadow-sm'
                      : 'text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900'
                    }
                  `}
                >
                  <tab.icon className="h-5 w-5 flex-shrink-0" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </aside>

          {/* Main Content */}
          <main className="lg:col-span-9 mt-6 lg:mt-0">
            <div className="bg-white shadow-sm ring-1 ring-secondary-200/60 rounded-2xl overflow-hidden">
              {/* Profile Tab */}
              {activeTab === 'profile' && (
                <div className="p-8 space-y-8">
                  <div className="border-b border-secondary-200 pb-6">
                    <h2 className="text-xl font-bold text-secondary-900">プロフィール設定</h2>
                    <p className="text-sm text-secondary-500 mt-2">あなたの基本情報を管理します</p>
                  </div>

                  <div className="flex items-center gap-8">
                    <div className="relative">
                      <div className="h-24 w-24 rounded-2xl bg-gradient-to-br from-primary-100 to-primary-50 flex items-center justify-center text-primary-600 text-3xl font-bold">
                        {user?.full_name?.charAt(0) || 'U'}
                      </div>
                      <button className="absolute -bottom-2 -right-2 h-8 w-8 rounded-full bg-primary-600 text-white flex items-center justify-center shadow-lg hover:bg-primary-500 transition-colors">
                        <CameraIcon className="h-4 w-4" />
                      </button>
                    </div>
                    <div>
                      <p className="text-lg font-semibold text-secondary-900">{user?.full_name || 'ユーザー'}</p>
                      <p className="text-sm text-secondary-500">{user?.email || 'email@example.com'}</p>
                      <p className="text-xs text-secondary-400 mt-1">JPG, PNG, GIF 対応（最大1MB）</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-8 sm:grid-cols-2">
                    <div>
                      <label className="block text-sm font-semibold text-secondary-900 mb-2">氏名</label>
                      <input
                        type="text"
                        defaultValue={user?.full_name || ''}
                        className="block w-full rounded-xl border-0 px-4 py-3.5 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 focus:ring-2 focus:ring-primary-500 text-base transition-shadow"
                        placeholder="山田 太郎"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-secondary-900 mb-2">メールアドレス</label>
                      <input
                        type="email"
                        defaultValue={user?.email || ''}
                        className="block w-full rounded-xl border-0 px-4 py-3.5 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 focus:ring-2 focus:ring-primary-500 text-base transition-shadow"
                        placeholder="email@example.com"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-secondary-900 mb-2">役割</label>
                      <input
                        type="text"
                        defaultValue={user?.role || ''}
                        disabled
                        className="block w-full rounded-xl border-0 px-4 py-3.5 text-secondary-500 bg-secondary-50 shadow-sm ring-1 ring-inset ring-secondary-200 text-base cursor-not-allowed"
                      />
                      <p className="mt-2 text-xs text-secondary-400">役割は管理者のみ変更可能です</p>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-secondary-900 mb-2">部署</label>
                      <input
                        type="text"
                        defaultValue="投資部門"
                        className="block w-full rounded-xl border-0 px-4 py-3.5 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 focus:ring-2 focus:ring-primary-500 text-base transition-shadow"
                        placeholder="所属部署"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Notifications Tab */}
              {activeTab === 'notifications' && (
                <div className="p-8 space-y-8">
                  <div className="border-b border-secondary-200 pb-6">
                    <h2 className="text-xl font-bold text-secondary-900">通知設定</h2>
                    <p className="text-sm text-secondary-500 mt-2">通知の受信方法を設定します</p>
                  </div>

                  <div className="space-y-2">
                    {[
                      { id: 'email_case', label: '新規案件の通知', desc: '新しい案件が作成されたとき', enabled: true },
                      { id: 'email_conflict', label: '矛盾検出の通知', desc: 'データの矛盾が検出されたとき', enabled: true },
                      { id: 'email_approval', label: '承認依頼の通知', desc: '承認が必要なアクションがあるとき', enabled: false },
                      { id: 'email_report', label: 'レポート完成の通知', desc: 'レポートの生成が完了したとき', enabled: true },
                    ].map((item) => (
                      <div key={item.id} className="flex items-center justify-between py-5 px-4 rounded-xl hover:bg-secondary-50/50 transition-colors">
                        <div>
                          <p className="text-base font-semibold text-secondary-900">{item.label}</p>
                          <p className="text-sm text-secondary-500 mt-0.5">{item.desc}</p>
                        </div>
                        <button
                          type="button"
                          className={`relative inline-flex h-7 w-12 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                            item.enabled ? 'bg-primary-600' : 'bg-secondary-300'
                          }`}
                        >
                          <span className={`pointer-events-none relative inline-block h-6 w-6 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                            item.enabled ? 'translate-x-5' : 'translate-x-0'
                          }`} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Security Tab */}
              {activeTab === 'security' && (
                <div className="p-8 space-y-8">
                  <div className="border-b border-secondary-200 pb-6">
                    <h2 className="text-xl font-bold text-secondary-900">セキュリティ設定</h2>
                    <p className="text-sm text-secondary-500 mt-2">アカウントのセキュリティを管理します</p>
                  </div>

                  <div className="space-y-8">
                    <div>
                      <h3 className="text-base font-semibold text-secondary-900 mb-4">パスワード変更</h3>
                      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                        <div>
                          <label className="block text-sm font-medium text-secondary-700 mb-2">現在のパスワード</label>
                          <input
                            type="password"
                            placeholder="••••••••"
                            className="block w-full rounded-xl border-0 px-4 py-3.5 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 focus:ring-2 focus:ring-primary-500 text-base transition-shadow"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-secondary-700 mb-2">新しいパスワード</label>
                          <input
                            type="password"
                            placeholder="••••••••"
                            className="block w-full rounded-xl border-0 px-4 py-3.5 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 focus:ring-2 focus:ring-primary-500 text-base transition-shadow"
                          />
                        </div>
                      </div>
                    </div>

                    <div className="border-t border-secondary-200 pt-8">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="text-base font-semibold text-secondary-900">二要素認証</h3>
                          <p className="text-sm text-secondary-500 mt-1">アカウントのセキュリティを強化します</p>
                        </div>
                        <button className="inline-flex items-center rounded-xl bg-secondary-100 px-4 py-2.5 text-sm font-semibold text-secondary-900 hover:bg-secondary-200 transition-colors">
                          有効化する
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Preferences Tab */}
              {activeTab === 'preferences' && (
                <div className="p-8 space-y-8">
                  <div className="border-b border-secondary-200 pb-6">
                    <h2 className="text-xl font-bold text-secondary-900">環境設定</h2>
                    <p className="text-sm text-secondary-500 mt-2">アプリケーションの表示設定を変更します</p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between py-5 px-4 rounded-xl hover:bg-secondary-50/50 transition-colors">
                      <div>
                        <p className="text-base font-semibold text-secondary-900">言語</p>
                        <p className="text-sm text-secondary-500 mt-0.5">表示言語を選択します</p>
                      </div>
                      <select className="rounded-xl border-0 py-3 pl-4 pr-10 text-secondary-900 ring-1 ring-inset ring-secondary-300 focus:ring-2 focus:ring-primary-500 text-base appearance-none bg-white cursor-pointer">
                        <option>日本語</option>
                        <option>English</option>
                      </select>
                    </div>
                    <div className="flex items-center justify-between py-5 px-4 rounded-xl hover:bg-secondary-50/50 transition-colors">
                      <div>
                        <p className="text-base font-semibold text-secondary-900">タイムゾーン</p>
                        <p className="text-sm text-secondary-500 mt-0.5">日時の表示に使用するタイムゾーン</p>
                      </div>
                      <select className="rounded-xl border-0 py-3 pl-4 pr-10 text-secondary-900 ring-1 ring-inset ring-secondary-300 focus:ring-2 focus:ring-primary-500 text-base appearance-none bg-white cursor-pointer">
                        <option>Asia/Tokyo (JST)</option>
                        <option>UTC</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Save Button */}
              <div className="border-t border-secondary-200 px-8 py-6 bg-secondary-50/30 flex justify-end">
                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="inline-flex items-center rounded-xl bg-primary-600 px-6 py-3 text-base font-semibold text-white shadow-lg shadow-primary-500/25 hover:bg-primary-500 hover:shadow-xl hover:shadow-primary-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                >
                  {isSaving ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      保存中...
                    </>
                  ) : (
                    '変更を保存'
                  )}
                </button>
              </div>
            </div>
          </main>
        </div>
      </div>
    </Layout>
  )
}
