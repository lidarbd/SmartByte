/**
 * ProductCard Component
 * 
 * Displays a recommended product with details
 */

import type { Product } from '../../types/chat.types';
import { formatPrice } from '../../utils/formatters';

interface ProductCardProps {
  product: Product;
  isUpsell?: boolean;
}

export default function ProductCard({ product, isUpsell = false }: ProductCardProps) {
  return (
    <div className={`bg-white rounded-lg border-2 p-4 hover:shadow-md transition-shadow ${
      isUpsell ? 'border-amber-400 bg-amber-50' : 'border-gray-200'
    }`}>
      
      {/* Upsell badge */}
      {isUpsell && (
        <div className="inline-block bg-amber-500 text-white text-xs font-bold px-2 py-1 rounded mb-2">
          💡 מומלץ להוסיף
        </div>
      )}
      
      {/* Product name and brand */}
      <h3 className="font-semibold text-gray-900 mb-1">
        {product.name}
      </h3>
      {product.brand && (
        <p className="text-sm text-gray-600 mb-2">
          {product.brand}
        </p>
      )}
      
      {/* Price and stock */}
      <div className="flex items-center justify-between mt-3">
        <span className="text-lg font-bold text-indigo-600">
          {formatPrice(product.price)}
        </span>
        <span className={`text-sm ${product.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
          {product.stock > 0 ? `במלאי (${product.stock})` : 'אזל מהמלאי'}
        </span>
      </div>
      
      {/* Specs if available */}
      {product.specs && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
            {product.specs.cpu && (
              <div>
                <span className="font-medium">מעבד:</span> {product.specs.cpu}
              </div>
            )}
            {product.specs.ram_gb && (
              <div>
                <span className="font-medium">זיכרון:</span> {product.specs.ram_gb}GB
              </div>
            )}
            {product.specs.storage_gb && (
              <div>
                <span className="font-medium">אחסון:</span> {product.specs.storage_gb}GB
              </div>
            )}
            {product.specs.gpu && (
              <div>
                <span className="font-medium">GPU:</span> {product.specs.gpu}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}