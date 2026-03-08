import { useLivePortfolio } from '../hooks/useLivePortfolio';
import { AllocationPieChart } from './AllocationPieChart';
import { LiveNumber } from './LiveNumber';
import { LiveMetricSparkline } from './LiveMetricSparkline';
import { useMemo } from 'react';

function allocationToChartData(allocation: Record<string, number>) {
  return Object.entries(allocation)
    .filter(([, v]) => v > 0)
    .map(([name, value]) => ({ name, value: Math.round(value * 10) / 10 })
    )
    .sort((a, b) => b.value - a.value);
}

export function PortfolioReallocationDashboard() {
  const { current, recommended, metrics, table, colors, wsConnected, refetch } = useLivePortfolio();

  const currentData = useMemo(() => allocationToChartData(current), [current]);
  const recommendedData = useMemo(
    () => allocationToChartData(recommended),
    [recommended]
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-stone-700 pb-2">
        <h2 className="text-lg font-display font-semibold text-stone-300">
          Portfolio reallocation
        </h2>
        <button
          type="button"
          onClick={() => refetch()}
          className="text-xs text-amber-500 hover:text-amber-400 px-2 py-1 rounded hover:bg-stone-800"
        >
          Refresh
        </button>
      </div>

      {/* Top row: Current | Recommended pies + Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-4 bg-stone-900/80 rounded-xl border border-stone-700 p-4 flex flex-col items-center">
          <AllocationPieChart
            data={currentData}
            colors={colors}
            title="Current Portfolio"
            size={260}
          />
        </div>

        <div className="lg:col-span-4 bg-stone-900/80 rounded-xl border border-stone-700 p-4 flex flex-col items-center relative">
          <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-2 text-amber-500 hidden lg:block">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
          <AllocationPieChart
            data={recommendedData}
            colors={colors}
            title="2026 Resilient Portfolio"
            size={260}
          />
        </div>

        <div className="lg:col-span-4 bg-stone-900/80 rounded-xl border border-stone-700 p-5">
          <h3 className="text-sm font-display font-semibold text-stone-300 mb-4">
            Recommended Portfolio Metrics
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-baseline">
              <span className="text-stone-500 text-sm">Reward</span>
              <LiveNumber
                value={metrics?.reward ?? 0}
                suffix="%"
                delta={metrics?.rewardDelta}
                decimals={2}
                className="text-white font-semibold"
              />
            </div>
            <div className="flex justify-between items-baseline">
              <span className="text-stone-500 text-sm">Risk</span>
              <LiveNumber
                value={metrics?.risk ?? 0}
                suffix="%"
                delta={metrics?.riskDelta}
                decimals={2}
                className="text-white font-semibold"
              />
            </div>
            <div className="flex justify-between items-baseline">
              <span className="text-stone-500 text-sm">Sharpe Ratio</span>
              <LiveNumber
                value={metrics?.sharpe ?? 0}
                delta={metrics?.sharpeDelta}
                decimals={2}
                deltaDecimals={2}
                className="text-white font-semibold"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom row: Reallocation table + Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 bg-stone-900/80 rounded-xl border border-stone-700 overflow-hidden">
          <div className="px-4 py-3 border-b border-stone-700">
            <h3 className="text-sm font-display font-semibold text-stone-300">
              Asset reallocation (SAA vs TAA)
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-stone-500 border-b border-stone-700">
                  <th className="text-left py-3 px-4 font-medium">
                    Asset class
                  </th>
                  <th className="text-right py-3 px-4 font-medium">
                    SAA (%)
                  </th>
                  <th className="text-right py-3 px-4 font-medium">
                    TAA (%)
                  </th>
                  <th className="text-left py-3 px-4 font-medium">
                    Reasoning
                  </th>
                </tr>
              </thead>
              <tbody>
                {table.map((row) => (
                  <tr
                    key={row.assetClass}
                    className="border-b border-stone-800 hover:bg-stone-800/50"
                  >
                    <td className="py-3 px-4 text-stone-200">
                      {row.assetClass}
                    </td>
                    <td className="py-3 px-4 text-right text-stone-300">
                      {row.saa}%
                    </td>
                    <td className="py-3 px-4 text-right text-stone-300">
                      {row.taa}%
                    </td>
                    <td className="py-3 px-4 text-stone-400 max-w-xs">
                      {row.reasoning}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="lg:col-span-5 flex items-stretch">
          <div className="w-full bg-red-950/50 border border-red-900/60 rounded-xl p-5 flex items-center">
            <p className="text-red-200 text-sm leading-relaxed">
              Utilizing 20% Cash from the Old Portfolio towards Bonds & Private
              markets while maintaining some liquidity.
            </p>
          </div>
        </div>
      </div>

      {/* Live-updating metrics sparklines */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <LiveMetricSparkline
          label="Reward %"
          value={metrics?.reward ?? 0}
          color="#10b981"
        />
        <LiveMetricSparkline
          label="Risk %"
          value={metrics?.risk ?? 0}
          color="#f59e0b"
        />
        <LiveMetricSparkline
          label="Sharpe"
          value={metrics?.sharpe ?? 0}
          color="#6366f1"
        />
      </div>

      <div className="bg-stone-900/80 rounded-xl border border-stone-700 px-4 py-3 flex items-center justify-between flex-wrap gap-2">
        <span className="text-stone-500 text-xs">
          Macro themes driving reallocation: Fed pivot expectations, EM currency
          pressure, US inflation cycle. Metrics update every few seconds.
        </span>
        <span className="text-stone-600 text-xs">
          Data refreshes {wsConnected ? 'via WebSocket' : 'via polling'}.
        </span>
      </div>
    </div>
  );
}
