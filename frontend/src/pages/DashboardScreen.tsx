/**
 * DashboardScreen Component
 * 
 * Main admin dashboard with metrics, charts, and session history
 */

import { useEffect, useState } from 'react';
import Navbar from '../components/admin/Navbar';
import StatsCard from '../components/admin/StatsCard';
import SimpleLineChart from '../components/admin/SimpleLineChart';
import SimplePieChart from '../components/admin/SimplePieChart';
import SessionTable from '../components/admin/SessionTable';
import { 
  getDashboardStats,
  getDailyConsultations,
  getCustomerSegments,
  getSessionHistory 
} from '../services/adminService';
import type { DashboardStats, SessionHistory } from '../types/admin.types';

// Mock data for development (used as fallback if API fails)
const mockDailyData = [
  { date: '21/01', value: 12 },
  { date: '22/01', value: 19 },
  { date: '23/01', value: 15 },
  { date: '24/01', value: 25 },
  { date: '25/01', value: 22 },
  { date: '26/01', value: 30 },
  { date: '27/01', value: 28 },
];

const mockCustomerTypes = [
  { name: 'Student', value: 45 },
  { name: 'Gamer', value: 25 },
  { name: 'Engineer', value: 15 },
  { name: 'Business', value: 10 },
  { name: 'Other', value: 5 },
];

export default function DashboardScreen() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [dailyData, setDailyData] = useState<any[]>(mockDailyData);
  const [customerData, setCustomerData] = useState<any[]>(mockCustomerTypes);
  const [sessions, setSessions] = useState<SessionHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Load all data in parallel
      const [
        statsData,
        dailyConsultations,
        customerSegments,
        sessionHistoryData
      ] = await Promise.all([
        getDashboardStats().catch(() => null),
        getDailyConsultations(7).catch(() => []), // Last 7 days
        getCustomerSegments().catch(() => []),
        getSessionHistory({
          page: 1,
          per_page: 20,
        }).catch(() => ({ sessions: [], total: 0, page: 1, per_page: 20, total_pages: 0 })),
      ]);

      // Set stats
      if (statsData) {
        setStats(statsData);
      }

      // Transform and set daily data
      if (dailyConsultations && dailyConsultations.length > 0) {
        const transformed = dailyConsultations.map(item => ({
          date: new Date(item.date).toLocaleDateString('he-IL', { day: '2-digit', month: '2-digit' }),
          value: item.count,
        }));
        setDailyData(transformed);
      }

      // Transform and set customer segments
      if (customerSegments && customerSegments.length > 0) {
        const transformed = customerSegments.map(item => ({
          name: item.customer_type,
          value: item.count,
        }));
        setCustomerData(transformed);
      }

      // Set sessions
      if (sessionHistoryData && sessionHistoryData.sessions) {
        setSessions(sessionHistoryData.sessions);
      }

    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('שגיאה בטעינת נתונים');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <Navbar />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        
        {/* Error Message */}
        {error && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <p className="text-yellow-800">⚠️ {error}</p>
            <p className="text-yellow-700 text-sm mt-1">
              מציג נתוני דמו. ודא שהבקאנד רץ ומחובר.
            </p>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="סה״כ שיחות"
            value={stats?.total_sessions || 156}
            icon="💬"
            color="blue"
            trend={{ value: 12, isPositive: true }}
          />
          <StatsCard
            title="המלצות שניתנו"
            value={stats?.total_recommendations || 89}
            icon="🎯"
            color="green"
            trend={{ value: 8, isPositive: true }}
          />
          <StatsCard
            title="ממוצע הודעות"
            value={stats?.avg_messages_per_session?.toFixed(1) || '5.2'}
            icon="📊"
            color="purple"
          />
          <StatsCard
            title="שיעור המרה"
            value={stats?.conversion_rate ? `${stats.conversion_rate}%` : '94%'}
            icon="⭐"
            color="orange"
            trend={{ value: 3, isPositive: true }}
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <SimpleLineChart
            data={dailyData}
            title="שיחות יומיות (שבוע אחרון)"
            color="#6366f1"
          />
          <SimplePieChart
            data={customerData}
            title="התפלגות סוגי לקוחות"
          />
        </div>

        {/* Session History Table */}
        <SessionTable
          sessions={sessions}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}