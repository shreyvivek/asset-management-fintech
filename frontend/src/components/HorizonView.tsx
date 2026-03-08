import { useHorizon, type HorizonItem } from '../hooks/useHorizon';
import { useState } from 'react';

function Row({ item }: { item: HorizonItem }) {
  const up = item.deltaPct >= 0;
  return (
    <tr className="border-b border-stone-700 hover:bg-stone-800/50">
      <td className="py-3 px-4 font-medium text-stone-200">{item.ticker}</td>
      <td className="py-3 px-4 text-stone-300 tabular-nums">
        ${item.currentPrice.toFixed(2)}
      </td>
      <td className="py-3 px-4 text-stone-300 tabular-nums">
        ${item.macroAdjustedFairValue.toFixed(2)}
      </td>
      <td className={`py-3 px-4 tabular-nums font-medium ${up ? 'text-emerald-400' : 'text-red-400'}`}>
        {up ? '+' : ''}{item.deltaPct.toFixed(1)}%
      </td>
      <td className="py-3 px-4 text-stone-400 text-sm max-w-xs">{item.narrative}</td>
    </tr>
  );
}

export function HorizonView() {
  const { view, watchlist, loading, refetch, addTicker } = useHorizon();
  const [input, setInput] = useState('');
  const [adding, setAdding] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);

  const handleAdd = async () => {
    const t = input.trim().toUpperCase();
    if (!t) return;
    setAdding(true);
    setAddError(null);
    try {
      await addTicker(t);
      setInput('');
    } catch {
      setAddError('Failed to add ticker');
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="rounded-xl border border-stone-700 bg-stone-900/80 overflow-hidden">
      <div className="p-4 border-b border-stone-700 flex flex-wrap items-center gap-3">
        <h2 className="text-stone-300 font-display font-semibold">Horizon View</h2>
        <div className="flex gap-2 flex-wrap items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => { setInput(e.target.value); setAddError(null); }}
            onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
            placeholder="Ticker (e.g. AAPL)"
            className="bg-stone-800 border border-stone-600 rounded px-3 py-1.5 text-sm text-stone-200 placeholder-stone-500 w-28"
            disabled={adding}
          />
          <button
            type="button"
            onClick={handleAdd}
            disabled={adding || !input.trim()}
            className="px-3 py-1.5 rounded bg-amber-600 hover:bg-amber-500 disabled:opacity-50 disabled:pointer-events-none text-white text-sm font-medium"
          >
            {adding ? 'Adding…' : 'Add'}
          </button>
          <button
            type="button"
            onClick={() => refetch()}
            className="text-xs text-stone-500 hover:text-stone-400 px-2 py-1 rounded hover:bg-stone-800"
          >
            Refresh
          </button>
        </div>
        {addError && <p className="text-red-400 text-xs w-full">{addError}</p>}
      </div>
      <div className="overflow-x-auto">
        {loading ? (
          <p className="p-4 text-stone-500 text-sm">Loading…</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-stone-500 border-b border-stone-700">
                <th className="text-left py-3 px-4 font-medium">Ticker</th>
                <th className="text-right py-3 px-4 font-medium">Price</th>
                <th className="text-right py-3 px-4 font-medium">Macro FV</th>
                <th className="text-right py-3 px-4 font-medium">Δ%</th>
                <th className="text-left py-3 px-4 font-medium">Narrative</th>
              </tr>
            </thead>
            <tbody>
              {view.map((item) => (
                <Row key={item.ticker} item={item} />
              ))}
            </tbody>
          </table>
        )}
      </div>
      {view.length === 0 && !loading && (
        <p className="p-4 text-stone-500 text-sm">Add tickers to see macro-adjusted fair values.</p>
      )}
    </div>
  );
}
