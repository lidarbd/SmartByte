/**
 * TopProductsTable Component
 *
 * Displays the top recommended products with their recommendation counts
 */

import type { ProductStats } from '../../types/admin.types';

interface TopProductsTableProps {
  products: ProductStats[];
  isLoading?: boolean;
}

export default function TopProductsTable({ products, isLoading }: TopProductsTableProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-900">מוצרים מומלצים ביותר</h2>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">טוען נתונים...</div>
        </div>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-900">מוצרים מומלצים ביותר</h2>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">אין נתונים להצגה</div>
        </div>
      </div>
    );
  }

  // Find max count for bar width calculation
  const maxCount = Math.max(...products.map(p => p.recommendation_count));

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">מוצרים מומלצים ביותר</h2>
        <span className="text-sm text-gray-500">10 מוצרים מובילים</span>
      </div>

      <div className="space-y-3">
        {products.map((product, index) => {
          const barWidth = (product.recommendation_count / maxCount) * 100;

          return (
            <div key={index} className="group">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 text-xs font-semibold">
                    {index + 1}
                  </span>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium text-gray-900">
                      {product.product_name}
                    </span>
                    <span className="text-xs text-gray-500">{product.brand}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-indigo-600">
                    {product.recommendation_count}
                  </span>
                  <span className="text-xs text-gray-500">המלצות</span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${barWidth}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {products.length}
            </div>
            <div className="text-xs text-gray-500">מוצרים מוצגים</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {products.reduce((sum, p) => sum + p.recommendation_count, 0)}
            </div>
            <div className="text-xs text-gray-500">סה"כ המלצות</div>
          </div>
        </div>
      </div>
    </div>
  );
}
