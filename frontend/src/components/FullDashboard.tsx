import { useState } from 'react';
import { PortfolioReallocationDashboard } from './PortfolioReallocationDashboard';
import { MacroHeatMap } from './MacroHeatMap';
import { LivePulseFeed } from './LivePulseFeed';
import { HorizonView } from './HorizonView';
import { useLivePortfolio } from '../hooks/useLivePortfolio';

type Tab = 'reallocation' | 'intelligence';

export function FullDashboard() {
  const [tab, setTab] = useState<Tab>('reallocation');
  const { wsConnected } = useLivePortfolio();

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 border-b border-stone-700 bg-stone-950/95 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="font-display font-bold text-xl text-white">
              MIVE — Macro-Intelligence & Valuation Engine
            </h1>
            <p className="text-stone-500 text-xs mt-0.5">
              Signal over noise · Evidence-grounding · Red-teaming
            </p>
          </div>
          <div className="flex items-center gap-4">
            <nav className="flex gap-1">
              <button
                type="button"
                onClick={() => setTab('reallocation')}
                className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                  tab === 'reallocation'
                    ? 'bg-amber-600 text-white'
                    : 'text-stone-400 hover:text-stone-200'
                }`}
              >
                Reallocation
              </button>
              <button
                type="button"
                onClick={() => setTab('intelligence')}
                className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                  tab === 'intelligence'
                    ? 'bg-amber-600 text-white'
                    : 'text-stone-400 hover:text-stone-200'
                }`}
              >
                Intelligence
              </button>
            </nav>
            <div className="flex items-center gap-2">
              <span
                className={`h-2 w-2 rounded-full ${
                  wsConnected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
                }`}
              />
              <span className="text-xs text-stone-500">{wsConnected ? 'Live' : 'Polling'}</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6">
        {tab === 'reallocation' && <PortfolioReallocationDashboard />}
        {tab === 'intelligence' && (
          <div className="space-y-6">
            <MacroHeatMap />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <LivePulseFeed />
              <HorizonView />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
