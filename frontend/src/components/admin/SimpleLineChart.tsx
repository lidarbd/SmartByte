/**
 * SimpleLineChart Component
 * 
 * Line chart for showing trends over time (e.g., daily conversations)
 */

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface DataPoint {
  date: string;
  value: number;
}

interface SimpleLineChartProps {
  data: DataPoint[];
  title: string;
  color?: string;
}

export default function SimpleLineChart({ 
  data, 
  title,
  color = '#6366f1' 
}: SimpleLineChartProps) {
  
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      
      {/* Title */}
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      
      {/* Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="date" 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke={color}
            strokeWidth={3}
            dot={{ fill: color, r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}