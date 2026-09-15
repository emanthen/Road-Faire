import { describe, expect, it } from "vitest";
import { formatUSD } from "@/lib/money";

describe("formatUSD", () => {
  it("formats whole dollars", () => {
    expect(formatUSD(60000)).toBe("$600.00");
  });

  it("formats cents", () => {
    expect(formatUSD(150)).toBe("$1.50");
  });

  it("formats zero", () => {
    expect(formatUSD(0)).toBe("$0.00");
  });
});
