import { useState } from 'react'
import IssueDetailModal from './IssueDetailModal'

export default function IssuesTable({ issues, scanId, feedbacks = {}, onFeedbackSubmit }) {
  const [selectedIssue, setSelectedIssue] = useState(null)
  const [rowComments, setRowComments] = useState({})

  const handleCommentChange = (index, value) => {
    setRowComments(prev => ({
      ...prev,
      [index]: value
    }))
  }

  const severityConfig = {
    critique: { label: 'Critique', dot: 'bg-critical', bg: 'bg-critical/10', text: 'text-critical' },
    majeur:   { label: 'Majeur',   dot: 'bg-major', bg: 'bg-major/10', text: 'text-major' },
    mineur:   { label: 'Mineur',   dot: 'bg-minor', bg: 'bg-minor/10', text: 'text-minor' },
  }

  return (
    <div className="animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-sand-title flex items-center gap-2">
          <svg className="w-5 h-5 text-sand-title" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          Problèmes de Sécurité
        </h2>
        <span className="text-sm text-sand-text/80">{issues.length} problème{issues.length > 1 ? 's' : ''} détecté{issues.length > 1 ? 's' : ''}</span>
      </div>

      <div className="glass rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-sand-border">
                <th className="text-left px-5 py-3.5 text-xs font-semibold text-sand-text/80 uppercase tracking-wider">Fichier</th>
                <th className="text-left px-5 py-3.5 text-xs font-semibold text-sand-text/80 uppercase tracking-wider">Ligne</th>
                <th className="text-left px-5 py-3.5 text-xs font-semibold text-sand-text/80 uppercase tracking-wider">Type</th>
                <th className="text-left px-5 py-3.5 text-xs font-semibold text-sand-text/80 uppercase tracking-wider">Sévérité</th>
                <th className="text-left px-5 py-3.5 text-xs font-semibold text-sand-text/80 uppercase tracking-wider">Verdict (HITL)</th>
                <th className="text-right px-5 py-3.5 text-xs font-semibold text-sand-text/80 uppercase tracking-wider">Détails</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-sand-border/50">
              {issues.map((issue, index) => {
                const sev = severityConfig[issue.gravite] || severityConfig.mineur
                const findingId = index.toString()
                const feedback = feedbacks[findingId]
                const commentText = rowComments[index] || ''
                return (
                  <tr
                    key={index}
                    onClick={() => setSelectedIssue(issue)}
                    className={`cursor-pointer transition-colors duration-200 group ${index % 2 === 0 ? 'bg-sand-row1' : 'bg-sand-row2'} hover:brightness-95`}
                  >
                    <td className="px-5 py-4">
                      <span className="text-sand-btn-hover font-medium group-hover:text-sand-title transition-colors">
                        {issue.fichier}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <span className="text-sand-text font-mono text-xs bg-sand-border/30 px-2 py-0.5 rounded">
                        :{issue.ligne}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-sand-text">
                      {issue.type ? issue.type.replace(/_/g, ' ') : ''}
                    </td>
                    <td className="px-5 py-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold ${sev.bg} ${sev.text}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${sev.dot}`}></span>
                        {sev.label}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      {issue.source === 'ia' ? (
                        feedback ? (
                          <div className="flex flex-col gap-1 items-start" onClick={(e) => e.stopPropagation()}>
                            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold ${
                              feedback.corrected_verdict === 'TP'
                                ? 'bg-minor/15 text-minor border border-minor/30'
                                : 'bg-critical/15 text-critical border border-critical/30'
                            } border`}>
                              {feedback.corrected_verdict === 'TP' ? (
                                <>
                                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                  </svg>
                                  Accepté (TP)
                                </>
                              ) : (
                                <>
                                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                  </svg>
                                  Rejeté (FP)
                                </>
                              )}
                            </span>
                            {feedback.comment && (
                              <span className="text-[10px] text-sand-text/60 italic max-w-[150px] truncate" title={feedback.comment}>
                                "{feedback.comment}"
                              </span>
                            )}
                          </div>
                        ) : (
                          <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                            <input
                              type="text"
                              placeholder="Commentaire..."
                              value={commentText}
                              onChange={(e) => handleCommentChange(index, e.target.value)}
                              className="px-2 py-1 text-xs border border-sand-border/70 rounded-lg bg-sand-card text-sand-text focus:outline-none focus:ring-1 focus:ring-sand-title w-28 placeholder:text-sand-text/40 font-medium"
                            />
                            <button
                              onClick={() => onFeedbackSubmit(findingId, issue.source || 'ia', 'TP', commentText)}
                              className="px-2 py-1 rounded-lg bg-minor/15 text-minor text-xs font-bold hover:bg-minor hover:text-white transition-colors border border-minor/30 active:scale-95"
                              title="Valider le verdict de l'IA (True Positive)"
                            >
                              Valider
                            </button>
                            <button
                              onClick={() => onFeedbackSubmit(findingId, issue.source || 'ia', 'FP', commentText)}
                              className="px-2 py-1 rounded-lg bg-critical/15 text-critical text-xs font-bold hover:bg-critical hover:text-white transition-colors border border-critical/30 active:scale-95"
                              title="Rejeter le verdict de l'IA (False Positive)"
                            >
                              Rejeter
                            </button>
                          </div>
                        )
                      ) : (
                        <span className="text-xs text-sand-text/40 italic">N/A (Statique)</span>
                      )}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setSelectedIssue(issue)
                        }}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sand-btn/40 text-sand-title text-xs font-semibold hover:bg-sand-border hover:text-sand-btn-hover transition-colors shadow-sm border border-sand-border/50"
                        title="Voir explication et patch"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Détails
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {selectedIssue && (
        <IssueDetailModal
          issue={selectedIssue}
          onClose={() => setSelectedIssue(null)}
        />
      )}
    </div>
  )
}
