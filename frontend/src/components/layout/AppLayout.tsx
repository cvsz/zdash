import type { ReactNode } from 'react';import Sidebar from './Sidebar';import Topbar from './Topbar';
export default function AppLayout({children}:{children:ReactNode}){return <div className='min-h-screen flex'><Sidebar/><main className='flex-1'><Topbar/><div className='p-4'>{children}</div></main></div>}
