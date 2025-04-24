import { CopilotChat } from "@copilotkit/react-ui";

export default function Main() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
      <header className="flex items-center justify-center py-4 bg-gradient-to-r from-indigo-700 via-indigo-800 to-indigo-900 text-white shadow-lg">
        <h1 className="text-3xl font-extrabold">Sourcerer</h1>
      </header>
      <main className="flex items-center justify-center p-6">
        <div className="w-full max-w-4xl bg-white rounded-2xl shadow-xl h-[calc(100vh-80px)] overflow-hidden border border-gray-200">
          <div className="h-full p-4 overflow-auto">
            <CopilotChat className="h-full rounded-lg" />
          </div>
        </div>
      </main>
    </div>
  );
}
