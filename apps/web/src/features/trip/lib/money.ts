const symbols: Record<string, string> = { JPY: "¥", PHP: "₱", USD: "$" };

export function formatMoney(currency: string, amount: number) {
  const formatted = new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2,
  }).format(amount);
  return `${symbols[currency] ?? ""}${formatted}`;
}
