import { describe, expect, test, vi } from "vitest";
import * as bridgeModule from "../src/bridge";

describe("Forge desktop bridge", () => {
  test("exposes a versioned request bridge without implementing agent logic", async () => {
    expect(bridgeModule.FORGE_DESKTOP_PROTOCOL_VERSION).toBe("1.0");
    expect(bridgeModule.createForgeBridge).toBeTypeOf("function");

    const invoke = vi.fn().mockResolvedValue({
      protocol_version: "1.0",
      ok: true,
      result: { state: "RECEIVE" },
    });
    const bridge = bridgeModule.createForgeBridge(invoke);
    const response = await bridge.request("run_status", { run_id: "run-1" });

    expect(invoke).toHaveBeenCalledWith("forge_request", {
      request: {
        protocol_version: "1.0",
        operation: "run_status",
        payload: { run_id: "run-1" },
      },
    });
    expect(response.result).toEqual({ state: "RECEIVE" });
  });

  test("rejects protocol mismatches returned by the backend", async () => {
    expect(bridgeModule.createForgeBridge).toBeTypeOf("function");
    const bridge = bridgeModule.createForgeBridge(
      vi.fn().mockResolvedValue({ protocol_version: "2.0", ok: true, result: {} }),
    );
    await expect(bridge.request("health", {})).rejects.toThrow(/protocol/i);
  });
});
