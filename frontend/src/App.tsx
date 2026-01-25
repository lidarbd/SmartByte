

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-indigo-600 mb-4">
          Hello World! 👋
        </h1>
        <p className="text-xl text-gray-700">
          SmartByte Frontend is running successfully
        </p>
        <div className="mt-8 flex gap-4 justify-center">
          <div className="bg-green-500 text-white px-4 py-2 rounded-lg">
            ✓ React
          </div>
          <div className="bg-blue-500 text-white px-4 py-2 rounded-lg">
            ✓ TypeScript
          </div>
          <div className="bg-purple-500 text-white px-4 py-2 rounded-lg">
            ✓ Tailwind CSS
          </div>
        </div>
      </div>
    </div>
  )
}

export default App