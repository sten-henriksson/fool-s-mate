import { useCallback } from "react";

interface LogEntry {
  timestamp: string;
  title: string;
  content: string;
}

interface ApiResponse<T = any> {
  status: string;
  message?: string;
  result?: T;
  logs?: LogEntry[];
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = "") {
    this.baseUrl = baseUrl;
  }

  private async fetchWithAuth<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      credentials: "include", // Include cookies for session auth
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Request failed");
    }

    return response.json();
  }

  // Session Management
  async createSession(apiKey: string): Promise<ApiResponse> {
    return this.fetchWithAuth<ApiResponse>("/api-keys/session", {
      method: "POST",
      headers: {
        "X-API-Key": apiKey,
      },
    });
  }

  async verifySession(): Promise<ApiResponse> {
    return this.fetchWithAuth<ApiResponse>("/api-keys/verify-session");
  }

  // API Key Management
  async verifyApiKey(apiKey: string): Promise<ApiResponse> {
    return this.fetchWithAuth<ApiResponse>("/api-keys/verify", {
      method: "POST",
      headers: {
        "X-API-Key": apiKey,
      },
    });
  }

  async createApiKey(userId: string, apiKey: string): Promise<ApiResponse> {
    return this.fetchWithAuth<ApiResponse>("/api-keys", {
      method: "POST",
      headers: {
        "X-API-Key": apiKey,
      },
      body: JSON.stringify({ user_id: userId }),
    });
  }

  async deleteApiKey(apiKey: string): Promise<ApiResponse> {
    return this.fetchWithAuth<ApiResponse>("/api-keys", {
      method: "DELETE",
      headers: {
        "X-API-Key": apiKey,
      },
    });
  }

  // Kali Infer
  async startKaliInfer(additionalPrompt: string): Promise<ApiResponse> {
    return this.fetchWithAuth<ApiResponse>("/start-kali-infer", {
      method: "POST",
      body: JSON.stringify({ additional_prompt: additionalPrompt }),
    });
  }

  // Logs
  async getLogs(): Promise<ApiResponse<{ logs: LogEntry[] }>> {
    return this.fetchWithAuth<ApiResponse<{ logs: LogEntry[] }>>("/get-logs");
  }
}

// React Hook for using the API client
export const useApiClient = () => {
  const apiClient = new ApiClient();

  return {
    createSession: useCallback(
      (apiKey: string) => apiClient.createSession(apiKey),
      []
    ),
    verifySession: useCallback(() => apiClient.verifySession(), []),
    verifyApiKey: useCallback(
      (apiKey: string) => apiClient.verifyApiKey(apiKey),
      []
    ),
    createApiKey: useCallback(
      (userId: string, apiKey: string) => apiClient.createApiKey(userId, apiKey),
      []
    ),
    deleteApiKey: useCallback(
      (apiKey: string) => apiClient.deleteApiKey(apiKey),
      []
    ),
    startKaliInfer: useCallback(
      (additionalPrompt: string) => apiClient.startKaliInfer(additionalPrompt),
      []
    ),
    getLogs: useCallback(() => apiClient.getLogs(), []),
  };
};

export default ApiClient;
