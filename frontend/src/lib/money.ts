/** Never do arithmetic here — the backend fees/planner engines own the math (Decimal). */
export function formatUSD(cents: number): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(
    cents / 100
  );
}
