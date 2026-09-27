import { describe, expect, it } from "vitest";
import { formatMoney } from "./money";

describe("formatMoney", () => {
  it("prefixes the currency symbol", () => {
    expect(formatMoney("JPY", 1200)).toBe("¥1,200");
    expect(formatMoney("USD", 12.5)).toBe("$12.5");
  });
});
