import { Route, Switch } from "wouter";
import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { useApiClient, LogEntry } from "./api_client";
 
const App = () => {
  const [apiKey, setApiKey] = useState("");
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [, setLocation] = useLocation();
  const { createSession, getLogs } = useApiClient();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      console.log(apiKey)
      await createSession(apiKey);
      setLocation("/");
      fetchLogs();
    } catch (error) {
      alert("Login failed. Please check your API key.");
    }
  };
  // fetch logs every3 sec AI!
  useEffect(() => {
    const interval = setInterval(() => {
      fetchLogs();
    }, 3000);

    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, []);

  const fetchLogs = async () => {
    try {
      const response = await getLogs();
      setLogs(response.logs || []);
    } catch (error) {
      console.error("Failed to fetch logs:", error);
    }
  };

  return (
    <>
      <Switch>
        <Route path="/">
          <div className="min-h-screen p-4 bg-gray-50">
            <h1 className="text-2xl font-bold mb-4">Logs</h1>
            <div className="space-y-2">
              {logs.map((log, index) => (
                <div key={index} className="p-3 bg-white rounded-lg shadow-sm">
                  <p className="text-sm text-gray-500">{log.timestamp}</p>
                  <p className="font-medium">{log.title}</p>
                  <p className="text-gray-600">{log.content}</p>
                </div>
              ))}
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
