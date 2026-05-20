import { useState } from 'react'
import Navbar from './components/Navbar'
import FileUpload from './components/FileUpload'
import SummaryCards from './components/SummaryCards'
import IssuesTable from './components/IssuesTable'
import SBOMTable from './components/SBOMTable'

const getGradeConfig = (grade) => {
  const g = (grade || 'A').toUpperCase()
  switch (g) {
    case 'A': return { color: '#10B981', bg: 'bg-emerald-500/10', text: 'text-emerald-500' }
    case 'B': return { color: '#0D9488', bg: 'bg-teal-500/10', text: 'text-teal-500' }
    case 'C': return { color: '#F59E0B', bg: 'bg-amber-500/10', text: 'text-amber-500' }
    case 'D': return { color: '#F97316', bg: 'bg-orange-500/10', text: 'text-orange-500' }
    case 'E': return { color: '#F43F5E', bg: 'bg-rose-500/10', text: 'text-rose-500' }
    case 'F': return { color: '#EF4444', bg: 'bg-red-500/10', text: 'text-red-500' }
    default:  return { color: '#9C9A6B', bg: 'bg-minor/10', text: 'text-minor' }
  }
}

function App() {
  const [analysisData, setAnalysisData] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [error, setError] = useState(null)
  const [feedbacks, setFeedbacks] = useState({})
  const [isExportingPdf, setIsExportingPdf] = useState(false)

  const exportJSON = () => {
    if (!analysisData) return
    const json = JSON.stringify(analysisData, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `rapport_${analysisData.scan_id || 'analysis'}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const exportPDF = async () => {
    setIsExportingPdf(true)
    try {
      const response = await fetch('http://localhost:5000/export/pdf')
      
      if (response.status === 404) {
        alert("Aucun rapport disponible. Veuillez d'abord analyser une APK.")
        return
      }

      if (!response.ok) {
        throw new Error(`Erreur serveur (${response.status})`)
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'rapport_secuapk.pdf'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error(err)
      alert("Une erreur s'est produite lors du téléchargement du PDF. Veuillez vérifier votre connexion au serveur backend.")
    } finally {
      setIsExportingPdf(false)
    }
  }

  const handleFileSelect = (file) => {
    setSelectedFile(file)
    setError(null)
  }

  const fetchFeedbacks = async (scanId) => {
    try {
      const response = await fetch(`http://localhost:5000/feedback/${scanId}`)
      if (response.ok) {
        const data = await response.json()
        const feedbackMap = {}
        data.forEach(f => {
          feedbackMap[f.finding_id] = {
            corrected_verdict: f.corrected_verdict,
            comment: f.comment
          }
        })
        setFeedbacks(feedbackMap)
      }
    } catch (err) {
      console.error("Erreur lors de la récupération des feedbacks:", err)
    }
  }

  const handleFeedbackSubmit = async (findingId, originalVerdict, correctedVerdict, comment) => {
    if (!analysisData || !analysisData.scan_id) return

    try {
      const response = await fetch('http://localhost:5000/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scan_id: analysisData.scan_id,
          finding_id: findingId,
          original_verdict: originalVerdict,
          corrected_verdict: correctedVerdict,
          comment: comment || '',
        }),
      })

      if (!response.ok) {
        throw new Error(`Erreur serveur (${response.status})`)
      }

      setFeedbacks(prev => ({
        ...prev,
        [findingId]: {
          corrected_verdict: correctedVerdict,
          comment: comment
        }
      }))
    } catch (err) {
      console.error(err)
      alert("Impossible d'enregistrer le feedback. Vérifiez la connexion avec le serveur.")
    }
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return
    setIsAnalyzing(true)
    setError(null)
    setFeedbacks({})

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch('http://localhost:5000/analyze', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Erreur du serveur (${response.status})`)
      }

      const data = await response.json()
      setAnalysisData(data)
      setShowResults(true)
      if (data.scan_id) {
        await fetchFeedbacks(data.scan_id)
      }
    } catch (err) {
      console.error(err)
      setError("Impossible de contacter le serveur d'analyse. Vérifiez que le backend est bien lancé sur http://localhost:5000.")
      setShowResults(false)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const totalIssues = analysisData ? (analysisData.summary.critique + analysisData.summary.majeur + analysisData.summary.mineur) : 0

  return (
    <div className="min-h-screen bg-sand-bg">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Section */}
        <section className="text-center py-6">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-sand-title mb-2">
            Analysez la sécurité de votre{' '}
            <span className="text-sand-btn-hover">
              application mobile
            </span>
          </h2>
          <p className="text-sand-text/80 max-w-2xl mx-auto">
            Téléversez votre fichier APK pour détecter les vulnérabilités cryptographiques,
            les dépendances à risque et recevoir des recommandations de correction.
          </p>
        </section>

        {/* Upload Zone */}
        <section>
          <FileUpload onFileSelect={handleFileSelect} />
          
          {error && (
            <div className="mt-4 max-w-2xl mx-auto p-4 bg-critical/10 border border-critical/20 rounded-xl flex items-start gap-3">
              <svg className="w-5 h-5 text-critical shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-critical font-medium">{error}</p>
            </div>
          )}

          {selectedFile && !showResults && (
            <div className="mt-4 flex justify-center">
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className={`
                  inline-flex items-center gap-2 px-8 py-3 rounded-xl font-semibold text-sm
                  transition-all duration-200
                  ${isAnalyzing
                    ? 'bg-sand-border/50 text-sand-text cursor-wait'
                    : 'bg-sand-btn text-sand-btn-hover shadow-sm border border-sand-border hover:bg-sand-border active:scale-95'
                  }
                `}
              >
                {isAnalyzing ? (
                  <>
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Analyse en cours...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    Lancer l'analyse
                  </>
                )}
              </button>
            </div>
          )}
        </section>

        {/* Results */}
        {showResults && analysisData && (
          <>
            {/* Divider */}
            <div className="flex items-center gap-4">
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-sand-border to-transparent" />
              <span className="text-xs font-semibold text-sand-title uppercase tracking-widest">
                Résultats de l'analyse
              </span>
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-sand-border to-transparent" />
            </div>

            {/* Scan ID Banner */}
            {analysisData.scan_id && (
              <div className="flex justify-center animate-fade-in-up" style={{ animationDelay: '0.05s' }}>
                <div className="glass rounded-xl px-4 py-2 text-xs font-mono text-sand-text/80 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-minor animate-pulse"></span>
                  <span>ID d'analyse : <strong className="text-sand-title">{analysisData.scan_id}</strong></span>
                </div>
              </div>
            )}

            {/* Summary */}
            <section>
              <SummaryCards summary={analysisData.summary} />
            </section>

            {/* Score Ring */}
            {(() => {
              const globalScoreObj = analysisData.global_score || {
                score: Math.max(0, Math.round(((10 - totalIssues) / 10) * 100)),
                grade: 'B',
                raw: 0
              }
              const score = globalScoreObj.score
              const grade = globalScoreObj.grade
              const rawScore = globalScoreObj.raw
              const gradeConfig = getGradeConfig(grade)

              return (
                <section className="flex justify-center">
                  <div className="glass rounded-2xl p-6 flex items-center gap-6 animate-fade-in-up" style={{ animationDelay: '0.15s' }}>
                    <div className="relative w-24 h-24">
                      <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="42" fill="none" stroke="var(--color-sand-border)" strokeWidth="8" />
                        <circle
                          cx="50" cy="50" r="42" fill="none"
                          stroke={gradeConfig.color} strokeWidth="8"
                          strokeLinecap="round"
                          strokeDasharray={`${(score / 100) * 264} 264`}
                          className="transition-all duration-1000"
                        />
                      </svg>
                      <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className={`text-3xl font-black leading-none ${gradeConfig.text}`}>{grade}</span>
                        <span className="text-[10px] text-sand-text/70 uppercase tracking-wider font-semibold mt-1">{score}/100</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-lg font-bold text-sand-title">Score de Sécurité</p>
                      <p className="text-sm text-sand-text mt-1">
                        Classification : <strong className={gradeConfig.text}>{grade}</strong> ({score}/100)
                      </p>
                      <p className="text-xs text-sand-text/60 mt-0.5">Valeur brute calculée : {rawScore}</p>
                    </div>
                  </div>
                </section>
              )
            })()}

            {/* Issues Table */}
            <section>
              <IssuesTable
                issues={analysisData.issues || []}
                scanId={analysisData.scan_id}
                feedbacks={feedbacks}
                onFeedbackSubmit={handleFeedbackSubmit}
              />
            </section>

            {/* SBOM Table */}
            <section>
              <SBOMTable sbom={analysisData.sbom || []} />
            </section>

            {/* Export */}
            <section className="flex justify-center gap-4 pb-8 animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
              <button
                onClick={exportJSON}
                className="
                  inline-flex items-center gap-2 px-6 py-3 rounded-[30px]
                  bg-sand-btn text-sand-title font-semibold text-sm
                  shadow-sm border border-sand-border
                  hover:bg-sand-border hover:text-sand-btn-hover
                  active:scale-95
                  transition-all duration-200
                "
              >
                📄 Exporter JSON
              </button>
              <button
                onClick={exportPDF}
                disabled={isExportingPdf}
                className={`
                  inline-flex items-center gap-2 px-6 py-3 rounded-[30px]
                  bg-sand-btn text-sand-title font-semibold text-sm
                  shadow-sm border border-sand-border
                  hover:bg-sand-border hover:text-sand-btn-hover
                  active:scale-95
                  transition-all duration-200
                  ${isExportingPdf ? 'opacity-70 cursor-wait' : ''}
                `}
              >
                {isExportingPdf ? (
                  <>
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Téléchargement...
                  </>
                ) : (
                  <>📑 Exporter PDF</>
                )}
              </button>
            </section>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-sand-border py-6">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-xs text-sand-text/60">
            SecurAPK © 2026 — Outil d'analyse de sécurité des applications mobiles Android
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App

