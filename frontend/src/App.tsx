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
          <div className="min-h-screen p-4 bg-black font-mono text-green-400">
            <h1 className="text-2xl font-bold mb-4 text-green-400">> LOGS_VIEWER.EXE</h1>
            <div className="mb-6 space-y-2">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={additionalPrompt}
                  onChange={(e) => setAdditionalPrompt(e.target.value)}
                  placeholder="> ENTER ADDITIONAL PROMPT FOR KALI INFER"
                  className="flex-1 px-3 py-2 bg-black border-2 border-green-400 rounded-none text-green-400 placeholder-green-600 focus:outline-none focus:ring-0 focus:border-green-400"
                />
                <button
                  onClick={handleStartKaliInfer}
                  disabled={isLoading}
                  className="px-4 py-2 bg-black border-2 border-green-400 text-green-400 rounded-none hover:bg-green-400 hover:text-black focus:outline-none focus:ring-0 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? "> PROCESSING..." : "> EXECUTE"}
                </button>
              </div>
              <div className="flex gap-4 items-center">
                {Object.entries(visibleTypes).map(([type, checked]) => (
                  <label key={type} className="flex items-center gap-1">
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={(e) => setVisibleTypes(prev => ({...prev, [type]: e.target.checked}))}
                      className="w-4 h-4 bg-black border-2 border-green-400 rounded-none text-green-400 focus:ring-0"
                    />
                    <span className="text-sm text-green-400">> {type.toUpperCase()}</span>
                  </label>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              {logs
                .filter(log => visibleTypes[log.type as keyof typeof visibleTypes])
                .map((log, index) => {
                // Update log border colors
                let borderColor = "border-green-400";
                if (log.type === "task") {
                  borderColor = "border-blue-400";
                } else if (log.type === "markdown") {
                  borderColor = "border-yellow-400";
                } else if (log.type === "code") {
                  borderColor = "border-purple-400";
                }

                return (
                  <div key={index} className={`p-3 bg-black border-2 ${borderColor}`}>
                    <div className="flex items-center justify-between text-sm text-green-400">
                      <span>> {getRelativeTime(log.timestamp)}</span>
                      <span className={`px-2 py-1 text-xs font-medium border-2 ${borderColor} bg-black`}>
                        > {log.type.toUpperCase()}
                      </span>
                    </div>
                    <p className="font-medium mt-1 text-green-400">> {log.title}</p>
                    <p className="text-green-400">> {log.content}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </Route>
        <Route path="/login">
          <div className="min-h-screen flex items-center justify-center p-4 bg-black">
            <div className="w-full max-w-sm">
              <h1 className="text-2xl font-bold mb-6 text-center text-green-400">> LOGIN.EXE</h1>
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label htmlFor="api-key" className="block text-sm font-medium text-green-400">
                    > API KEY
                  </label>
                  <input
                    id="api-key"
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    className="mt-1 block w-full px-3 py-2 bg-black border-2 border-green-400 rounded-none text-green-400 placeholder-green-600 focus:outline-none focus:ring-0 focus:border-green-400"
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="w-full px-4 py-2 bg-black border-2 border-green-400 text-green-400 rounded-none hover:bg-green-400 hover:text-black focus:outline-none focus:ring-0"
                >
                  > AUTHENTICATE
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
