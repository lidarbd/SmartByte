/**
 * SimplePieChart Component
 * 
 * Pie chart for showing distribution (e.g., customer types)
 */

import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DataPoint {
  name: string;
  value: number;
}

interface SimplePieChartProps {
  data: DataPoint[];
  title: string;
}

// Color palette for different segments
const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6'];

export default function SimplePieChart({ data, title }: SimplePieChartProps) {
  
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      
      {/* Title */}
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      
      {/* Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${((percent ?? 0) * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}