import { useThemes, type Theme } from '../hooks/useThemes';

function HeatBadge({ theme }: { theme: Theme }) {
  const isHot = theme.heat >= 70;
  const isWarm = theme.heat >= 40 && theme.heat < 70;
  const color = isHot ? 'bg-red-600' : isWarm ? 'bg-amber-500' : 'bg-sky-600';
  const trajectoryIcon =
    theme.trajectory === 'heating' ? '↑' : theme.trajectory === 'cooling' ? '↓' : '→';
  const trajectoryColor =
    theme.trajectory === 'heating' ? 'text-red-400' : theme.trajectory === 'cooling' ? 'text-sky-400' : 'text-stone-400';

  return (
    <div
      className={`rounded-lg border border-stone-600 p-3 ${isHot ? 'ring-1 ring-red-500/50' : ''}`}
    >
      <div className="flex items-center justify-between gap-2">
        <div>
          <p className="text-stone-200 text-sm font-medium">{theme.name}</p>
          <p className="text-stone-500 text-xs">{theme.region}</p>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={`text-xs font-semibold ${trajectoryColor}`}>{trajectoryIcon}</span>
          <span className={`px-2 py-0.5 rounded text-xs font-semibold text-white ${color}`}>
            {theme.heat}
          </span>
        </div>
      </div>
      {theme.eventCount != null && theme.eventCount > 0 && (
        <p className="text-stone-600 text-xs mt-1">{theme.eventCount} events (48h)</p>
      )}
    </div>
  );
}

export function MacroHeatMap() {
  const { themes, loading, refetch } = useThemes();

  if (loading) {
    return (
      <div className="rounded-xl border border-stone-700 bg-stone-900/80 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-stone-300 font-display font-semibold">MacroHeat Map</h2>
          <button type="button" onClick={() => refetch()} className="text-xs text-amber-500 hover:text-amber-400 px-2 py-1 rounded hover:bg-stone-800">Refresh</button>
        </div>
        <p className="text-stone-500 text-sm">Loading themes…</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-stone-700 bg-stone-900/80 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-stone-300 font-display font-semibold">MacroHeat Map</h2>
        <button type="button" onClick={() => refetch()} className="text-xs text-amber-500 hover:text-amber-400 px-2 py-1 rounded hover:bg-stone-800">Refresh</button>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {themes.map((t) => (
          <HeatBadge key={t.id} theme={t} />
        ))}
      </div>
    </div>
  );
}
