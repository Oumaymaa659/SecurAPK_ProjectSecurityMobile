import { useEffect } from 'react'

export default function IssueDetailModal({ issue, onClose }) {
  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  if (!issue) return null

  const severityConfig = {
    critique: { label: 'Critique', bg: 'bg-critical/15', text: 'text-critical', border: 'border-critical/30' },
    majeur:   { label: 'Majeur',   bg: 'bg-major/15', text: 'text-major', border: 'border-major/30' },
    mineur:   { label: 'Mineur',   bg: 'bg-minor/15', text: 'text-minor', border: 'border-minor/30' },
  }
  const sev = severityConfig[issue.gravite] || severityConfig.mineur

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

      {/* Modal */}
      <div
        className="relative w-full max-w-2xl rounded-2xl bg-sand-card border border-sand-border shadow-2xl overflow-hidden animate-fade-in-up"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-sand-border">
          <div className="flex items-center gap-3">
            <span className={`px-2.5 py-1 rounded-lg text-xs font-bold uppercase ${sev.bg} ${sev.text} ${sev.border} border`}>
              {sev.label}
            </span>
            <h2 className="text-lg font-semibold text-sand-title">{issue.type.replace(/_/g, ' ')}</h2>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-sand-text/60 hover:text-sand-btn-hover hover:bg-sand-border/50 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-5 max-h-[70vh] overflow-y-auto">
          {/* Location */}
          <div className="flex items-center gap-4 text-sm">
            <span className="flex items-center gap-1.5 text-sand-text/80">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="text-sand-btn-hover font-medium">{issue.fichier}</span>
            </span>
            <span className="flex items-center gap-1.5 text-sand-text/80">
              Ligne <span className="text-sand-title font-medium">{issue.ligne}</span>
            </span>
          </div>

          {/* Risk Explanation */}
          <div>
            <h3 className="text-sm font-semibold text-sand-title uppercase tracking-wider mb-2 flex items-center gap-2">
              <svg className="w-4 h-4 text-critical" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              Explication du risque
            </h3>
            <p className="text-sm text-sand-text leading-relaxed bg-sand-bg rounded-xl p-4 border border-sand-border">
              {issue.explication}
            </p>
          </div>

          {/* Recommended Patch */}
          <div>
            <h3 className="text-sm font-semibold text-sand-title uppercase tracking-wider mb-2 flex items-center gap-2">
              <svg className="w-4 h-4 text-minor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Correction recommandée
            </h3>
            <pre className="bg-minor/10 border border-minor/20 rounded-xl p-4 text-sm text-minor font-mono overflow-x-auto">
              <code>{issue.patch}</code>
            </pre>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-sand-border flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-sand-btn border border-sand-border text-sand-title text-sm font-medium hover:bg-sand-border hover:text-sand-btn-hover transition-colors"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  )
}
