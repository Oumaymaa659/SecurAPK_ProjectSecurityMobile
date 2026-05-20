import { useState } from 'react'

export default function Navbar() {
  return (
    <nav className="glass sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo + Title */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-sand-btn flex items-center justify-center shadow-sm border border-sand-border">
              <svg className="w-5 h-5 text-sand-btn-hover" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-sand-title">
                Secur<span className="text-sand-btn-hover">APK</span>
              </h1>
              <p className="text-[10px] text-sand-text/70 -mt-1 tracking-wider uppercase">
                Analyse de Sécurité Mobile
              </p>
            </div>
          </div>

          {/* Status Badge */}
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-minor/10 border border-minor/30">
              <span className="w-2 h-2 rounded-full bg-minor animate-pulse"></span>
              <span className="text-xs font-medium text-minor">Analyse prête</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
