/**
 * EmptyState Component
 * 
 * Shows welcome message and suggestions when chat is empty
 */


interface EmptyStateProps {
  onSuggestionClick: (suggestion: string) => void;
}

export default function EmptyState({ onSuggestionClick }: EmptyStateProps) {
  const suggestions = [
    'אני מחפש מחשב נייד לעבודה',
    'צריך מחשב גיימינג חזק',
    'מחשב ללימודים באוניברסיטה',
    'מה המחשב הכי טוב עד 5000 ₪?',
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full py-12 px-4">
      
      {/* Welcome message */}
      <div className="text-center mb-8">
        <div className="text-6xl mb-4">💻</div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          ברוכים הבאים ל-SmartByte
        </h1>
        <p className="text-gray-600 max-w-md">
          אני כאן לעזור לך למצוא את המחשב המושלם לצרכים שלך.
          שאל אותי כל שאלה!
        </p>
      </div>
      
      {/* Suggestion chips */}
      <div className="w-full max-w-2xl">
        <p className="text-sm text-gray-500 mb-3 text-center">
          💡 רעיונות לשאלות:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => onSuggestionClick(suggestion)}
              className="bg-white border-2 border-gray-200 rounded-lg p-4 text-right hover:border-indigo-500 hover:bg-indigo-50 transition-all"
            >
              <span className="text-gray-700">{suggestion}</span>
            </button>
          ))}
        </div>
      </div>
      
      {/* Features */}
      <div className="grid grid-cols-3 gap-8 mt-12 max-w-2xl">
        <div className="text-center">
          <div className="text-3xl mb-2">🤖</div>
          <p className="text-sm text-gray-600">AI מתקדם</p>
        </div>
        <div className="text-center">
          <div className="text-3xl mb-2">💰</div>
          <p className="text-sm text-gray-600">המלצות מותאמות</p>
        </div>
        <div className="text-center">
          <div className="text-3xl mb-2">⚡</div>
          <p className="text-sm text-gray-600">תשובות מהירות</p>
        </div>
      </div>
    </div>
  );
}