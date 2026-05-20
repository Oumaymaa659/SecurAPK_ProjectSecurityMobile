export default function SBOMTable({ sbom }) {
  return (
    <div className="animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-sand-title flex items-center gap-2">
          <svg className="w-5 h-5 text-sand-title" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          Dépendances (SBOM)
        </h2>
        <span className="text-sm text-sand-text/80">{sbom.length} bibliothèque{sbom.length > 1 ? 's' : ''}</span>
      </div>

      <div className="glass rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-sand-border">
                <th className="text-left px-5 py-3.5 text-xs font-semibold text-sand-text/80 uppercase tracking-wider">Bibliothèque</th>
                <th className="text-left px-5 py-3.5 text-xs font-semibold text-sand-text/80 uppercase tracking-wider">Version</th>
                <th className="text-left px-5 py-3.5 text-xs font-semibold text-sand-text/80 uppercase tracking-wider">Licence</th>
                <th className="text-left px-5 py-3.5 text-xs font-semibold text-sand-text/80 uppercase tracking-wider">Vulnérabilités</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-sand-border/50">
              {sbom.map((dep, index) => (
                <tr key={index} className={`transition-colors duration-200 ${index % 2 === 0 ? 'bg-sand-row1' : 'bg-sand-row2'} hover:brightness-95`}>
                  <td className="px-5 py-4">
                    <span className="text-sand-text font-medium">{dep.library}</span>
                  </td>
                  <td className="px-5 py-4">
                    <span className="text-sand-text/80 font-mono text-xs bg-sand-border/30 px-2 py-0.5 rounded">
                      {dep.version}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    {dep.license ? (
                      <a
                        href="#"
                        onClick={(e) => {
                          e.preventDefault();
                          const query = encodeURIComponent(`${dep.library} license`);
                          window.open(`https://www.google.com/search?q=${query}`, '_blank');
                        }}
                        className="text-xs px-2.5 py-1 rounded-lg bg-sand-border/20 border border-sand-border/50 font-medium hover:bg-sand-border/40 transition-colors"
                        style={{ color: '#A67C52', textDecoration: 'underline', cursor: 'pointer' }}
                        title={`Chercher la licence de ${dep.library} sur Google`}
                      >
                        {dep.license}
                      </a>
                    ) : (
                      <span className="text-sand-text/60 text-xs px-2.5 py-1 rounded-lg bg-sand-border/10 border border-sand-border/30 font-medium">
                        À vérifier
                      </span>
                    )}
                  </td>
                  <td className="px-5 py-4">
                    {dep.vulnerabilities.length > 0 ? (
                      <div className="flex flex-wrap gap-1.5">
                        {dep.vulnerabilities.map((cve) => (
                          <span
                            key={cve}
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-mono font-medium bg-critical/10 text-critical border border-critical/20"
                          >
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                            </svg>
                            {cve}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs text-minor">
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        Aucune
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
