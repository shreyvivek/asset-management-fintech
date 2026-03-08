import { useRef, useEffect, useState } from 'react';
import { AreaChart, Area, ResponsiveContainer, XAxis, YAxis } from 'recharts';

const MAX_POINTS = 24;

interface LiveMetricSparklineProps {
  value: number;
  label: string;
  color?: string;
  height?: number;
}

export function LiveMetricSparkline({
  value,
  label,
  color = '#10b981',
  height = 56,
}: LiveMetricSparklineProps) {
  const [series, setSeries] = useState<{ t: number; v: number }[]>([]);
  const prevRef = useRef(value);

  useEffect(() => {
    const next = { t: Date.now(), v: value };
    prevRef.current = value;
    setSeries((s) => {
      const nextSeries = [...s, next].slice(-MAX_POINTS);
      return nextSeries;
    });
  }, [value]);

  const data = series.map(({ t, v }) => ({ time: t, value: v }));

  return (
    <div className="rounded-lg bg-stone-800/50 p-2 border border-stone-700/50">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs text-stone-500">{label}</span>
        <span className="text-sm font-semibold text-stone-200 tabular-nums">
          {value.toFixed(2)}
        </span>
      </div>
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data} margin={{ top: 2, right: 2, left: 2, bottom: 2 }}>
          <defs>
            <linearGradient id={`grad-${label.replace(/\s/g, '-')}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.4} />
              <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <YAxis hide domain={['dataMin - 0.5', 'dataMax + 0.5']} />
          <XAxis hide dataKey="time" />
          <Area
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={1.5}
            fill={`url(#grad-${label.replace(/\s/g, '-')})`}
            isAnimationActive={true}
            animationDuration={300}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
