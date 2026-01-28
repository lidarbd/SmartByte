/**
 * SessionDetailsModal Component
 *
 * Displays full conversation history and recommendations for a session
 */

import { useEffect, useState } from 'react';
import { getSessionDetails } from '../../services/adminService';
import { formatDate } from '../../utils/formatters';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface Recommendation {
  product_id: number;
  product_name: string;
  product_price: number;
  upsell_product_id?: number | null;
  upsell_product_name?: string | null;
  recommendation_text: string;
  timestamp: string;
}

interface SessionDetails {
  session_id: string;
  customer_type: string | null;
  started_at: string;
  ended_at: string | null;
  messages: Message[];
  recommendations: Recommendation[];
}

interface SessionDetailsModalProps {
  sessionId: string;
  onClose: () => void;
}

export default function SessionDetailsModal({ sessionId, onClose }: SessionDetailsModalProps) {
  const [details, setDetails] = useState<SessionDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSessionDetails();
  }, [sessionId]);

  const loadSessionDetails = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getSessionDetails(sessionId);
      setDetails(data);
    } catch (err) {
      console.error('Error loading session details:', err);
      setError('שגיאה בטעינת פרטי השיחה');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">

        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">פרטי שיחה</h2>
            <p className="text-sm text-gray-500 font-mono mt-1">{sessionId}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-gray-500">טוען פרטי שיחה...</div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
              {error}
            </div>
          ) : details ? (
            <div className="space-y-6">

              {/* Session Info */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">סוג לקוח</p>
                    <p className="font-medium text-gray-900">
                      {details.customer_type || 'לא זוהה'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">תאריך התחלה</p>
                    <p className="font-medium text-gray-900">
                      {formatDate(details.started_at, 'FULL')}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">סה"כ הודעות</p>
                    <p className="font-medium text-gray-900">{details.messages.length}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">המלצות</p>
                    <p className="font-medium text-gray-900">{details.recommendations.length}</p>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">היסטוריית שיחה</h3>
                <div className="space-y-3">
                  {details.messages.map((message, index) => (
                    <div
                      key={index}
                      className={`rounded-lg p-4 ${
                        message.role === 'user'
                          ? 'bg-blue-50 border border-blue-200'
                          : 'bg-green-50 border border-green-200'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className={`text-xs font-semibold uppercase ${
                          message.role === 'user' ? 'text-blue-600' : 'text-green-600'
                        }`}>
                          {message.role === 'user' ? '👤 לקוח' : '🤖 אסיסטנט'}
                        </span>
                        <span className="text-xs text-gray-500">
                          {formatDate(message.timestamp, 'TIME_ONLY')}
                        </span>
                      </div>
                      <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
                        {message.content}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendations */}
              {details.recommendations.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">המלצות שניתנו</h3>
                  <div className="space-y-4">
                    {details.recommendations.map((rec, index) => (
                      <div
                        key={index}
                        className="bg-purple-50 border border-purple-200 rounded-lg p-4"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <p className="font-semibold text-purple-900">{rec.product_name}</p>
                            <p className="text-sm text-purple-600">₪{rec.product_price.toLocaleString()}</p>
                          </div>
                          <span className="text-xs text-gray-500">
                            {formatDate(rec.timestamp, 'FULL')}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 mb-2 whitespace-pre-wrap">
                          {rec.recommendation_text}
                        </p>
                        {rec.upsell_product_name && (
                          <div className="mt-2 pt-2 border-t border-purple-200">
                            <p className="text-xs text-purple-600 font-medium">
                              🎁 Upsell: {rec.upsell_product_name}
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            סגור
          </button>
        </div>

      </div>
    </div>
  );
}
