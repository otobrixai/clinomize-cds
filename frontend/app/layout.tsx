// frontend/app/layout.tsx
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Clinomize-CDS',
  description: 'Multi-module clinical decision support platform for transfusion medicine and cardiac care. Evidence-based recommendations for blood transfusion and acute coronary syndromes.',
  keywords: ['clinical decision support', 'CDS', 'transfusion', 'cardiology', 'ACS', 'blood transfusion', 'STEMI', 'NSTEMI'],
  authors: [{ name: 'Clinomize-CDS Team' }],
  openGraph: {
    type: 'website',
    title: 'Clinomize-CDS',
    description: 'Evidence-based clinical decision support for healthcare professionals',
    siteName: 'Clinomize-CDS',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <meta name="theme-color" content="#0ea5e9" />
      </head>
      <body className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 font-sans">
        <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))] opacity-10"></div>
        <div className="relative">
          {children}
        </div>
      </body>
    </html>
  )
}