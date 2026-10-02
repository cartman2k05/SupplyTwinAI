/**
 * Reconnecting WebSocket Client with Automatic Exponential Backoff and HTTP Polling Fallback
 */

export class SimulationWebSocket {
  constructor(options = {}) {
    this.onTelemetry = options.onTelemetry || (() => {});
    this.onDisruption = options.onDisruption || (() => {});
    this.onStatusChange = options.onStatusChange || (() => {});

    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 1000;
    this.pollingIntervalId = null;
    this.isPolling = false;
    this.isClosedManually = false;
  }

  connect() {
    this.isClosedManually = false;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host || 'localhost:8000';
    // Handle Vite dev server port 5173 vs API port 8000
    const wsHost = host.includes('5173') ? 'localhost:8000' : host;
    const wsUrl = `${protocol}//${wsHost}/api/v1/simulation/ws`;

    this.onStatusChange(this.reconnectAttempts > 0 ? 'reconnecting' : 'connecting');

    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        this.reconnectAttempts = 0;
        this.stopPolling();
        this.onStatusChange('connected');
      };

      this.socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'telemetry' && payload.data) {
            this.onTelemetry(payload.data);
          } else if (payload.type === 'disruption_injected') {
            this.onDisruption(payload.event);
            if (payload.telemetry) {
              this.onTelemetry(payload.telemetry);
            }
          }
        } catch (err) {
          console.error('[WS] Error parsing WebSocket message:', err);
        }
      };

      this.socket.onclose = () => {
        if (this.isClosedManually) {
          this.onStatusChange('disconnected');
          return;
        }
        this.handleReconnect();
      };

      this.socket.onerror = () => {
        if (this.socket) {
          this.socket.close();
        }
      };
    } catch (err) {
      console.warn('[WS] Failed to instantiate WebSocket:', err);
      this.handleReconnect();
    }
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const timeout = Math.min(10000, this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1));
      this.onStatusChange('reconnecting');
      setTimeout(() => this.connect(), timeout);
    } else {
      console.warn('[WS] Max reconnect attempts reached. Falling back to HTTP polling.');
      this.startPolling();
    }
  }

  startPolling() {
    if (this.isPolling) return;
    this.isPolling = true;
    this.onStatusChange('polling');

    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/v1/simulation/status');
        if (response.ok) {
          const json = await response.json();
          if (json.data) {
            this.onTelemetry(json.data);
          }
        }
      } catch (err) {
        console.error('[WS-Fallback] HTTP polling error:', err);
      }
    };

    fetchStatus();
    this.pollingIntervalId = setInterval(fetchStatus, 5000);
  }

  stopPolling() {
    if (this.pollingIntervalId) {
      clearInterval(this.pollingIntervalId);
      this.pollingIntervalId = null;
    }
    this.isPolling = false;
  }

  disconnect() {
    this.isClosedManually = true;
    this.stopPolling();
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.onStatusChange('disconnected');
  }
}
