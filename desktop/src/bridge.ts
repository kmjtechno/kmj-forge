export const FORGE_DESKTOP_PROTOCOL_VERSION = "1.0" as const;

type InvokeFn = (command: string, args?: Record<string, unknown>) => Promise<unknown>;

export interface ForgeBridgeResponse<T = unknown> {
  protocol_version: string;
  ok: boolean;
  result: T;
  error?: { message?: string } | string;
}

export function createForgeBridge(invoke: InvokeFn) {
  return {
    async request<T = unknown>(operation: string, payload: Record<string, unknown>): Promise<ForgeBridgeResponse<T>> {
      const response = (await invoke("forge_request", {
        request: {
          protocol_version: FORGE_DESKTOP_PROTOCOL_VERSION,
          operation,
          payload,
        },
      })) as ForgeBridgeResponse<T>;

      if (response.protocol_version !== FORGE_DESKTOP_PROTOCOL_VERSION) {
        throw new Error(
          `Forge protocol mismatch: expected ${FORGE_DESKTOP_PROTOCOL_VERSION}, received ${response.protocol_version}`,
        );
      }
      if (!response.ok) {
        const message = typeof response.error === "string" ? response.error : response.error?.message;
        throw new Error(message || `Forge operation failed: ${operation}`);
      }
      return response;
    },
  };
}
