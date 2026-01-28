/**
 * SessionTable Component
 * 
 * Table displaying chat sessions with search and filtering
 */

import { useState } from 'react';
import { formatDate } from '../../utils/formatters';
import Input from '../common/Input';
import SessionDetailsModal from './SessionDetailsModal';
import type { SessionHistory } from '../../types/admin.types';

interface SessionTableProps {
  sessions: SessionHistory[];
  isLoading?: boolean;
}

export default function SessionTable({ sessions, isLoading }: SessionTableProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  // Filter sessions based on search and type
  const filteredSessions = sessions.filter((session) => {
    // Search filter
    const matchesSearch = 
      session.session_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (session.customer_type?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false);

    // Type filter
    const matchesType = 
      filterType === 'all' || 
      session.customer_type === filterType;

    return matchesSearch && matchesType;
  });

  // Get unique customer types for filter
  const customerTypes = ['all', ...new Set(sessions.map(s => s.customer_type).filter((type): type is string => type !== null))];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      
      {/* Header with Search and Filter */}
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">היסטוריית שיחות</h3>
        
        <div className="flex gap-4">
          {/* Search */}
          <div className="flex-1">
            <Input
              placeholder="חפש לפי Session ID או סוג לקוח..."
              value={searchQuery}
              onChange={setSearchQuery}
              fullWidth
            />
          </div>

          {/* Filter by Type */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {customerTypes.map((type) => (
              <option key={type} value={type}>
                {type === 'all' ? 'כל הסוגים' : type}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">טוען נתונים...</div>
        ) : filteredSessions.length === 0 ? (
          <div className="p-8 text-center text-gray-500">לא נמצאו שיחות</div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Session ID
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  סוג לקוח
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  הודעות
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  מוצרים שהומלצו
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  תאריך יצירה
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredSessions.map((session) => (
                <tr
                  key={session.session_id}
                  className="hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => setSelectedSessionId(session.session_id)}
                >
                  <td className="px-6 py-4 text-sm text-gray-900 font-mono">
                    {session.session_id.substring(0, 20)}...
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {session.customer_type ? (
                      <span className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs font-medium">
                        {session.customer_type}
                      </span>
                    ) : (
                      <span className="text-gray-400">לא זוהה</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {session.message_count}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {session.recommendation_count}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {formatDate(session.started_at, 'FULL')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-gray-200 text-sm text-gray-600">
        מציג {filteredSessions.length} מתוך {sessions.length} שיחות
      </div>

      {/* Session Details Modal */}
      {selectedSessionId && (
        <SessionDetailsModal
          sessionId={selectedSessionId}
          onClose={() => setSelectedSessionId(null)}
        />
      )}
    </div>
  );
}