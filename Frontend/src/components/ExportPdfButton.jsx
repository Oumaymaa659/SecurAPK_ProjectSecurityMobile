import { useState } from 'react'

export default function ExportPdfButton() {
  const [isExporting, setIsExporting] = useState(false)

  const handleExportPdf = async () => {
    setIsExporting(true)
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
      setIsExporting(false)
    }
  }

  return (
    <button
      onClick={handleExportPdf}
      disabled={isExporting}
      className={`
        inline-flex items-center gap-2 px-6 py-3 rounded-xl
        bg-sand-btn text-sand-title font-semibold text-sm
        shadow-sm border border-sand-border
        hover:bg-sand-border hover:text-sand-btn-hover
        active:scale-95
        transition-all duration-200
        ${isExporting ? 'opacity-75 cursor-not-allowed' : ''}
      `}
    >
      {isExporting ? (
        <>
          <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Téléchargement du PDF...
        </>
      ) : (
        <>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M9 15h6" />
          </svg>
          Exporter le rapport PDF
        </>
      )}
    </button>
  )
}
