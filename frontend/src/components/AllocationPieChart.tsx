import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';

interface AllocationPieChartProps {
  data: { name: string; value: number }[];
  colors: Record<string, string>;
  title: string;
  size?: number;
}

export function AllocationPieChart({
  data,
  colors,
  title,
  size = 280,
}: AllocationPieChartProps) {
  const entries = data.filter((d) => d.value > 0);

  return (
    <div className="flex flex-col items-center">
      <h3 className="text-sm font-display font-semibold text-stone-300 mb-2">
        {title}
      </h3>
      <ResponsiveContainer width="100%" height={size}>
        <PieChart>
          <Pie
            data={entries}
            cx="50%"
            cy="50%"
            innerRadius={size * 0.28}
            outerRadius={size * 0.42}
            paddingAngle={1}
            dataKey="value"
            nameKey="name"
            label={({ name, value }) => `${name} ${value}%`}
            labelLine={false}
          >
            {entries.map((entry, i) => (
              <Cell
                key={entry.name}
                fill={colors[entry.name] || `hsl(${(i * 60) % 360}, 60%, 50%)`}
                stroke="rgba(0,0,0,0.2)"
                strokeWidth={1}
              />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number) => [`${value}%`, 'Allocation']}
            contentStyle={{
              backgroundColor: 'rgb(28 25 23)',
              border: '1px solid rgb(68 64 60)',
              borderRadius: '8px',
            }}
            labelStyle={{ color: 'rgb(245 245 244)' }}
          />
          <Legend
            layout="vertical"
            align="right"
            verticalAlign="middle"
            formatter={(value) => (
              <span className="text-stone-400 text-xs">{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
