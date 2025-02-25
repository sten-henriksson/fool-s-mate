import { useCallback } from "react";

export interface LogEntry {
  timestamp: string;
  title: string;
  content: string;
  type: string;
}

export interface ApiResponse<T = any> {
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
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      // Handle 401 unauthorized
      if (response.status === 401) {
        throw new Error("401 Unauthorized");
      }

      // For successful POST requests that don't return JSON
      if (response.ok && options.method === "POST" && response.status === 200) {
        return true as T;
      }

      // Parse JSON for other responses
      const data = await response.json();
      
      // Check both HTTP status and API response status
      if (!response.ok || data.status !== "success") {
        throw new Error(data.message || "Request failed");
      }

      return data;
    } catch (error) {
      throw error;
    }
  }
  // Session Management
  async createSession(apiKey: string): Promise<boolean> {
    await this.fetchWithAuth("/api/api-keys/session", {
      method: "POST",
      headers: {
        "api-key": apiKey,
      },
    });
    return true;
  }

  async verifySession(): Promise<ApiResponse> {
    return this.fetchWithAuth<ApiResponse>("/api/api-keys/verify-session");
  }

  // API Key Management
  async verifyApiKey(apiKey: string): Promise<boolean> {
    await this.fetchWithAuth("/api/api-keys/verify", {
      method: "POST",
      headers: {
        "api-key": apiKey,
      },
    });
    return true;
  }

  async createApiKey(userId: string, apiKey: string): Promise<boolean> {
    await this.fetchWithAuth("/api/api-keys", {
      method: "POST",
      headers: {
        "api-key": apiKey,
      },
      body: JSON.stringify({ user_id: userId }),
    });
    return true;
  }

  async deleteApiKey(apiKey: string): Promise<boolean> {
    await this.fetchWithAuth("/api/api-keys", {
      method: "DELETE",
      headers: {
        "api-key": apiKey,
      },
    });
    return true;
  }

  // Kali Infer
  async startKaliInfer(additionalPrompt: string): Promise<boolean> {
    await this.fetchWithAuth("/api/start-kali-infer", {
      method: "POST",
      body: JSON.stringify({ additional_prompt: additionalPrompt }),
      headers: {
        "Content-Type": "application/json",
      },
    });
    return true;
  }

  // Logs
  async getLogs(): Promise<ApiResponse<{ logs: LogEntry[] }>> {
    return this.fetchWithAuth<ApiResponse<{ logs: LogEntry[] }>>("/api/get-logs");
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
