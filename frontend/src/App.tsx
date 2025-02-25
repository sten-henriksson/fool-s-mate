import { Route, Switch } from "wouter";
import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { useApiClient, LogEntry } from "./api_client";

const getRelativeTime = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  const days = Math.floor(diffInSeconds / (3600 * 24));
  const hours = Math.floor((diffInSeconds % (3600 * 24)) / 3600);
  const minutes = Math.floor((diffInSeconds % 3600) / 60);
  const seconds = diffInSeconds % 60;

  let result = '';
  if (days > 0) result += `${days}d `;
  if (hours > 0) result += `${hours}h `;
  if (minutes > 0) result += `${minutes}m `;
  result += `${seconds}s ago`;
  
  return result.trim();
};
 
const App = () => {
  const [apiKey, setApiKey] = useState("");
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [additionalPrompt, setAdditionalPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [, setLocation] = useLocation();
  const { createSession, getLogs, startKaliInfer } = useApiClient();
  const [visibleTypes, setVisibleTypes] = useState({
    task: true,
    markdown: true,
    code: true,
  });

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      console.log(apiKey)
      await createSession(apiKey);
      setLocation("/");
      fetchLogs();
    } catch (error) {
      console.log(error)
      alert("Login failed. Please check your API key.");
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await getLogs();
      setLogs(response.logs || []);
    } catch (error) {
      console.error("Failed to fetch logs:", error);
      // Check if error is 401 unauthorized
      if (error instanceof Error && error.message.includes("401")) {
        setLocation("/login");
      }
    }
  };

  useEffect(() => {
    const fetchInitialLogs = async () => {
      await fetchLogs();
    };
    fetchInitialLogs();

    const interval = setInterval(() => {
      fetchLogs();
    }, 3000);

    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, []);

  const handleStartKaliInfer = async () => {
    try {
      setIsLoading(true);
      await startKaliInfer(additionalPrompt);
      setAdditionalPrompt("");
      alert("Kali Infer started successfully!");
    } catch (error) {
      console.error("Failed to start Kali Infer:", error);
      alert("Failed to start Kali Infer. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Switch>
        <Route path="/">
          <div className="min-h-screen p-4 bg-gray-50">
            <h1 className="text-2xl font-bold mb-4">Logs</h1>
            <div className="mb-6 space-y-2">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={additionalPrompt}
                  onChange={(e) => setAdditionalPrompt(e.target.value)}
                  placeholder="Enter additional prompt for Kali Infer"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
                <button
                  onClick={handleStartKaliInfer}
                  disabled={isLoading}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? "Starting..." : "Start Kali Infer"}
                </button>
              </div>
              <div className="flex gap-4 items-center">
                <label className="flex items-center gap-1">
                  <input
                    type="checkbox"
                    checked={visibleTypes.task}
                    onChange={(e) => setVisibleTypes(prev => ({...prev, task: e.target.checked}))}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm">Tasks</span>
                </label>
                <label className="flex items-center gap-1">
                  <input
                    type="checkbox"
                    checked={visibleTypes.markdown}
                    onChange={(e) => setVisibleTypes(prev => ({...prev, markdown: e.target.checked}))}
                    className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                  />
                  <span className="text-sm">Markdown</span>
                </label>
                <label className="flex items-center gap-1">
                  <input
                    type="checkbox"
                    checked={visibleTypes.code}
                    onChange={(e) => setVisibleTypes(prev => ({...prev, code: e.target.checked}))}
                    className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                  />
                  <span className="text-sm">Code</span>
                </label>
              </div>
            </div>
            <div className="space-y-2">
              {logs
                .filter(log => visibleTypes[log.type as keyof typeof visibleTypes])
                .map((log, index) => {
                // Determine background color based on type
                let bgColor = "bg-white";
                if (log.type === "task") {
                  bgColor = "bg-blue-50";
                } else if (log.type === "markdown") {
                  bgColor = "bg-green-50";
                } else if (log.type === "code") {
                  bgColor = "bg-purple-50";
                }

                return (
                  <div key={index} className={`p-3 rounded-lg shadow-sm ${bgColor}`}>
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span>{getRelativeTime(log.timestamp)}</span>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        log.type === "task" ? "bg-blue-100 text-blue-800" :
                        log.type === "markdown" ? "bg-green-100 text-green-800" :
                        "bg-purple-100 text-purple-800"
                      }`}>
                        {log.type}
                      </span>
                    </div>
                    <p className="font-medium mt-1">{log.title}</p>
                    <p className="text-gray-600">{log.content}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </Route>
        <Route path="/login">
          <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
            <div className="w-full max-w-sm">
              <h1 className="text-2xl font-bold mb-6 text-center">Login</h1>
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label htmlFor="api-key" className="block text-sm font-medium text-gray-700">
                    API Key
                  </label>
                  <input
                    id="api-key"
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  Login
                </button>
              </form>
            </div>
          </div>
        </Route>
        <Route>404: No such page!</Route>
      </Switch>
    </>
  );
}
export default App;
