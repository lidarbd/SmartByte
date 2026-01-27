/**
 * FileUpload Component
 *
 * Component for uploading CSV files with products
 */

import { useState, useRef } from 'react';
import { uploadProductsCSV } from '../../services/adminService';

interface UploadResult {
  message: string;
  statistics: {
    total_rows: number;
    loaded: number;
    updated: number;
    skipped: number;
    errors: string[];
  };
}

export default function FileUpload() {
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.csv')) {
      setError('אנא בחר קובץ CSV בלבד');
      return;
    }

    setIsUploading(true);
    setError(null);
    setResult(null);

    try {
      const uploadResult = await uploadProductsCSV(file);
      setResult(uploadResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'שגיאה בהעלאת הקובץ');
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">העלאת מוצרים מקובץ CSV</h3>

      {/* Upload Button */}
      <div className="mb-4">
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileSelect}
          className="hidden"
        />
        <button
          onClick={handleButtonClick}
          disabled={isUploading}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          {isUploading ? (
            <>
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span>מעלה קובץ...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <span>בחר קובץ CSV</span>
            </>
          )}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">❌ {error}</p>
        </div>
      )}

      {/* Success Result */}
      {result && (
        <div className="space-y-4">
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800 font-medium">✅ {result.message}</p>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">סה"כ שורות</p>
              <p className="text-2xl font-bold text-gray-900">{result.statistics.total_rows}</p>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <p className="text-sm text-green-600">נטענו</p>
              <p className="text-2xl font-bold text-green-900">{result.statistics.loaded}</p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-600">עודכנו</p>
              <p className="text-2xl font-bold text-blue-900">{result.statistics.updated}</p>
            </div>
            <div className="p-3 bg-yellow-50 rounded-lg">
              <p className="text-sm text-yellow-600">דולגו</p>
              <p className="text-2xl font-bold text-yellow-900">{result.statistics.skipped}</p>
            </div>
          </div>

          {/* Errors List */}
          {result.statistics.errors && result.statistics.errors.length > 0 && (
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <h4 className="font-semibold text-yellow-900 mb-2">
                ⚠️ שגיאות ({result.statistics.errors.length})
              </h4>
              <ul className="text-sm text-yellow-800 space-y-1 max-h-40 overflow-y-auto">
                {result.statistics.errors.map((err, index) => (
                  <li key={index} className="font-mono text-xs">• {err}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Instructions */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-semibold text-blue-900 mb-2">📋 הוראות שימוש</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• הקובץ חייב להיות בפורמט CSV</li>
          <li>• עמודות נדרשות: SKU, Name, Brand, Type, Category, Price, Stock</li>
          <li>• מוצרים קיימים (לפי SKU) יעודכנו אוטומטית</li>
          <li>• שורות עם שגיאות ידולגו</li>
        </ul>
      </div>
    </div>
  );
}
