export default function SummaryCards({ summary }) {
  const cards = [
    {
      label: 'Critiques',
      count: summary.critique || 0,
      color: 'bg-critical',
      border: 'border-critical/20',
      text: 'text-critical',
      shadow: 'shadow-critical/10',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      ),
    },
    {
      label: 'Majeurs',
      count: summary.majeur || 0,
      color: 'bg-major',
      border: 'border-major/20',
      text: 'text-major',
      shadow: 'shadow-major/10',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    {
      label: 'Mineurs',
      count: summary.mineur || 0,
      color: 'bg-minor',
      border: 'border-minor/20',
      text: 'text-minor',
      shadow: 'shadow-minor/10',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
      {cards.map((card) => (
        <div
          key={card.label}
          className={`
            relative overflow-hidden rounded-2xl bg-sand-card border ${card.border}
            p-6 transition-all duration-300 hover:scale-[1.03] hover:shadow-xl ${card.shadow}
            group cursor-default
          `}
        >
          {/* Gradient accent line */}
          <div className={`absolute top-0 left-0 right-0 h-1 ${card.color}`} />

          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-sand-text/70 uppercase tracking-wider">{card.label}</p>
              <p className={`text-4xl font-extrabold mt-2 ${card.text}`}>{card.count}</p>
            </div>
            <div className={`${card.text} opacity-40 group-hover:opacity-80 transition-opacity duration-300`}>
              {card.icon}
            </div>
          </div>

          {/* Subtle background pattern */}
          <div className={`absolute -bottom-4 -right-4 w-24 h-24 rounded-full ${card.color} opacity-5 group-hover:opacity-10 transition-opacity duration-500`} />
        </div>
      ))}
    </div>
  )
}
