import { useState, useRef } from 'react'

export default function FileUpload({ onFileSelect }) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file && file.name.endsWith('.apk')) {
      setSelectedFile(file)
      onFileSelect?.(file)
    }
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
      onFileSelect?.(file)
    }
  }

  return (
    <div className="animate-fade-in-up">
      <div
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative group cursor-pointer rounded-2xl border-2 border-dashed p-8 text-center
          transition-all duration-300 ease-out bg-sand-drop-bg
          ${isDragOver
            ? 'border-sand-title scale-[1.02] bg-sand-border/20'
            : selectedFile
              ? 'border-minor/50 bg-minor/10'
              : 'border-sand-border hover:border-sand-title/50 hover:bg-sand-border/10'
          }
        `}
      >
        {/* Background gradient */}
        <div className="absolute inset-0 rounded-2xl bg-sand-border/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

        <input
          ref={fileInputRef}
          type="file"
          accept=".apk"
          className="hidden"
          onChange={handleFileChange}
        />

        <div className="relative z-10">
          {selectedFile ? (
            <>
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-minor/20 flex items-center justify-center">
                <svg className="w-8 h-8 text-minor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <p className="text-lg font-semibold text-minor">{selectedFile.name}</p>
              <p className="text-sm text-sand-text/80 mt-1">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} Mo — Prêt pour l'analyse
              </p>
            </>
          ) : (
            <>
              <div className={`
                w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center transition-all duration-300
                ${isDragOver ? 'bg-sand-border/30 scale-110' : 'bg-sand-border/20'}
              `}>
                <svg className={`w-8 h-8 transition-colors duration-300 ${isDragOver ? 'text-sand-title' : 'text-sand-text/80'}`}
                  fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <p className="text-lg font-semibold text-sand-title">
                {isDragOver ? "Déposez le fichier ici" : "Glissez-déposez votre fichier APK"}
              </p>
              <p className="text-sm text-sand-text/80 mt-1">
                ou <span className="text-sand-title hover:text-sand-btn-hover font-medium">parcourir</span> pour sélectionner
              </p>
              <p className="text-xs text-sand-text/60 mt-3">Formats supportés : .apk</p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
