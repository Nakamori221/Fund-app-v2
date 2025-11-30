import { Fragment, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import {
  Bars3Icon,
  XMarkIcon,
  HomeIcon,
  BriefcaseIcon,
  DocumentTextIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  CloudArrowUpIcon,
  DocumentChartBarIcon,
  ArrowsRightLeftIcon,
} from '@heroicons/react/24/outline'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'

const navigation = [
  { name: 'ダッシュボード', href: '/dashboard', icon: HomeIcon },
  { name: '案件管理', href: '/cases', icon: BriefcaseIcon },
  { name: '観察記録', href: '/observations', icon: DocumentTextIcon },
  { name: 'レポート', href: '/reports', icon: ChartBarIcon },
]

const demoNavigation = [
  { name: '資料アップロード', href: '/upload', icon: CloudArrowUpIcon },
  { name: 'ICレポート', href: '/report-preview', icon: DocumentChartBarIcon },
  { name: 'データフロー', href: '/data-flow', icon: ArrowsRightLeftIcon },
]

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

export default function Sidebar({ sidebarOpen, setSidebarOpen }: { sidebarOpen: boolean; setSidebarOpen: (open: boolean) => void }) {
  const location = useLocation()
  const { logout } = useAuthStore()

  return (
    <>
      <Transition.Root show={sidebarOpen} as={Fragment}>
        <Dialog as="div" className="relative z-50 lg:hidden" onClose={setSidebarOpen}>
          <Transition.Child
            as={Fragment}
            enter="transition-opacity ease-linear duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity ease-linear duration-300"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-secondary-900/80" />
          </Transition.Child>

          <div className="fixed inset-0 flex">
            <Transition.Child
              as={Fragment}
              enter="transition ease-in-out duration-300 transform"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="transition ease-in-out duration-300 transform"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <Dialog.Panel className="relative mr-16 flex w-full max-w-xs flex-1">
                <Transition.Child
                  as={Fragment}
                  enter="ease-in-out duration-300"
                  enterFrom="opacity-0"
                  enterTo="opacity-100"
                  leave="ease-in-out duration-300"
                  leaveFrom="opacity-100"
                  leaveTo="opacity-0"
                >
                  <div className="absolute left-full top-0 flex w-16 justify-center pt-5">
                    <button type="button" className="-m-2.5 p-2.5" onClick={() => setSidebarOpen(false)}>
                      <span className="sr-only">Close sidebar</span>
                      <XMarkIcon className="h-6 w-6 text-white" aria-hidden="true" />
                    </button>
                  </div>
                </Transition.Child>
                {/* Mobile Sidebar Content */}
                <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-secondary-900 px-6 pb-4 ring-1 ring-white/10">
                  <div className="flex h-16 shrink-0 items-center">
                    <div className="text-xl font-bold text-white tracking-wider">Fund IC</div>
                  </div>
                  <nav className="flex flex-1 flex-col">
                    <ul role="list" className="flex flex-1 flex-col gap-y-7">
                      <li>
                        <ul role="list" className="-mx-2 space-y-1">
                          {navigation.map((item) => (
                            <li key={item.name}>
                              <Link
                                to={item.href}
                                className={classNames(
                                  location.pathname === item.href
                                    ? 'bg-secondary-800 text-white'
                                    : 'text-secondary-400 hover:text-white hover:bg-secondary-800',
                                  'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold'
                                )}
                              >
                                <item.icon className="h-6 w-6 shrink-0" aria-hidden="true" />
                                {item.name}
                              </Link>
                            </li>
                          ))}
                        </ul>
                      </li>
                      <li className="mt-auto">
                        <Link
                          to="/settings"
                          className="group -mx-2 flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 text-secondary-400 hover:bg-secondary-800 hover:text-white"
                        >
                          <Cog6ToothIcon className="h-6 w-6 shrink-0" aria-hidden="true" />
                          設定
                        </Link>
                        <button
                          onClick={logout}
                          className="w-full text-left group -mx-2 flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 text-secondary-400 hover:bg-secondary-800 hover:text-white"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 shrink-0">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
                          </svg>
                          ログアウト
                        </button>
                      </li>
                    </ul>
                  </nav>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </Dialog>
      </Transition.Root>

      {/* Desktop Sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-secondary-900 px-6 pb-4">
          <div className="flex h-16 shrink-0 items-center">
             <div className="text-xl font-bold text-white tracking-wider flex items-center gap-2">
                <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold">F</span>
                </div>
                Fund IC Auto
             </div>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href
                            ? 'bg-secondary-800 text-white'
                            : 'text-secondary-400 hover:text-white hover:bg-secondary-800',
                          'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold transition-colors duration-200'
                        )}
                      >
                        <item.icon className="h-6 w-6 shrink-0" aria-hidden="true" />
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>
              <li>
                <div className="text-xs font-semibold leading-6 text-secondary-500 uppercase tracking-wider">デモ機能</div>
                <ul role="list" className="-mx-2 mt-2 space-y-1">
                  {demoNavigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href
                            ? 'bg-primary-600 text-white'
                            : 'text-secondary-400 hover:text-white hover:bg-secondary-800',
                          'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold transition-colors duration-200'
                        )}
                      >
                        <item.icon className="h-6 w-6 shrink-0" aria-hidden="true" />
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>
              <li className="mt-auto space-y-1">
                <Link
                  to="/settings"
                  className="group -mx-2 flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 text-secondary-400 hover:bg-secondary-800 hover:text-white transition-colors duration-200"
                >
                  <Cog6ToothIcon className="h-6 w-6 shrink-0" aria-hidden="true" />
                  設定
                </Link>
                 <button
                    onClick={logout}
                    className="w-full text-left group -mx-2 flex gap-x-3 rounded-md p-2 text-sm font-semibold leading-6 text-secondary-400 hover:bg-secondary-800 hover:text-white transition-colors duration-200"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 shrink-0">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
                    </svg>
                    ログアウト
                  </button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </>
  )
}

