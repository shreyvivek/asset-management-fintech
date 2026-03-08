import { useFeed, type FeedEvent } from '../hooks/useFeed';
import { useSimulate } from '../hooks/useSimulate';

function FeedItem({
  ev,
  onQuickReact,
}: {
  ev: FeedEvent;
  onQuickReact: (ev: FeedEvent) => void;
}) {
  const time = ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : '—';
  return (
    <div
      className="border-b border-stone-700/80 py-3 px-2 hover:bg-stone-800/50 rounded cursor-pointer group"
      onClick={() => onQuickReact(ev)}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-stone-200 text-sm font-medium group-hover:text-amber-400 transition-colors">
            {ev.title || 'No title'}
          </p>
          <p className="text-stone-500 text-xs mt-0.5">
            {ev.source} · {time}
            {ev.verified ? (
              <span className="ml-1 text-emerald-500">Verified</span>
            ) : null}
          </p>
        </div>
        <span className="text-stone-600 text-xs shrink-0">Click for analysis</span>
      </div>
    </div>
  );
}

export function LivePulseFeed() {
  const { feed, loading, refetch } = useFeed();
  const { result, loading: simLoading, error, run } = useSimulate();
  const handleQuickReact = (ev: FeedEvent) => {
    run(ev.id, { title: ev.title || '', body: ev.body, type: ev.type });
  };

  return (
    <div className="rounded-xl border border-stone-700 bg-stone-900/80 overflow-hidden flex flex-col max-h-[520px]">
      <div className="p-4 border-b border-stone-700 flex items-center justify-between">
        <h2 className="text-stone-300 font-display font-semibold">LivePulse Feed</h2>
        <button
          type="button"
          onClick={() => refetch()}
          className="text-xs text-amber-500 hover:text-amber-400 px-2 py-1 rounded hover:bg-stone-800"
        >
          Refresh
        </button>
      </div>
      <div className="flex-1 overflow-y-auto min-h-0">
        <div className="divide-y divide-stone-800">
          {loading ? (
            <p className="p-4 text-stone-500 text-sm">Loading feed…</p>
          ) : feed.length === 0 ? (
            <p className="p-4 text-stone-500 text-sm">No events yet. Ingestion may be running.</p>
          ) : (
            feed.map((ev) => (
              <FeedItem key={ev.id} ev={ev} onQuickReact={handleQuickReact} />
            ))
          )}
        </div>
      </div>
      {error && (
        <div className="p-3 bg-red-900/30 border-t border-red-800 text-red-300 text-sm">
          {error}
        </div>
      )}
      {simLoading && (
        <div className="p-3 bg-stone-800/80 text-stone-400 text-sm border-t border-stone-700">
          Running agent simulation…
        </div>
      )}
      {result && !simLoading && (
        <div className="p-4 bg-stone-800/80 border-t border-stone-700 space-y-3">
          <p className="text-stone-400 text-xs font-medium">Risk chain</p>
          <ul className="text-stone-300 text-sm space-y-1">
            {result.riskChain?.map((r) => (
              <li key={r.order}>
                {r.order}. {r.implication} <span className="text-stone-500">({r.assetClass})</span>
              </li>
            ))}
          </ul>
          <p className="text-stone-400 text-xs font-medium mt-2">Agents</p>
          <div className="space-y-1">
            {result.agents?.map((a) => (
              <p key={a.id} className="text-stone-300 text-sm">
                <span className="text-stone-500">{a.name}:</span> {a.analysis}
              </p>
            ))}
          </div>
          {result.debater && (
            <>
              <p className="text-amber-400 text-xs font-medium">Debater</p>
              <p className="text-stone-400 text-sm">{result.debater}</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
