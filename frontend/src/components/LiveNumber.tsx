import { useState, useEffect, useRef } from 'react';

interface LiveNumberProps {
  value: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
  delta?: number;
  deltaDecimals?: number;
  animate?: boolean;
}

export function LiveNumber({
  value,
  decimals = 2,
  prefix = '',
  suffix = '',
  className = '',
  delta,
  deltaDecimals = 2,
  animate = true,
}: LiveNumberProps) {
  const [display, setDisplay] = useState(value);
  const prevRef = useRef(value);
  const [direction, setDirection] = useState<'up' | 'down' | null>(null);

  useEffect(() => {
    if (!animate) {
      setDisplay(value);
      return;
    }
    const prev = prevRef.current;
    if (value !== prev) {
      setDirection(value > prev ? 'up' : 'down');
      prevRef.current = value;
    }
    setDisplay(value);
  }, [value, animate]);

  return (
    <span className={`inline-flex items-baseline gap-1 ${className}`}>
      <span
        className={
          direction
            ? `animate-${direction === 'up' ? 'tick-up' : 'tick-down'}`
            : ''
        }
      >
        {prefix}
        {display.toFixed(decimals)}
        {suffix}
      </span>
      {delta != null && (
        <span
          className={
            delta >= 0
              ? 'text-emerald-400 text-sm font-medium'
              : 'text-red-400 text-sm font-medium'
          }
        >
          {delta >= 0 ? '+' : ''}
          {delta.toFixed(deltaDecimals)}%
        </span>
      )}
    </span>
  );
}
