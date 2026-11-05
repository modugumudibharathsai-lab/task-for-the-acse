export { cn } from "cn";

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function calculateConsecutiveClassesNeeded(
  attended: number,
  total: number,
  targetPercentage: number = 75
): number {
  const currentPct = (attended / total) * 100;
  if (currentPct >= targetPercentage) return 0;

  // (attended + x) / (total + x) >= targetPercentage / 100
  // 100 * attended + 100x >= target * total + target * x
  // (100 - target) * x >= target * total - 100 * attended
  const targetFraction = targetPercentage / 100;
  const needed = Math.ceil((targetFraction * total - attended) / (1 - targetFraction));
  return Math.max(0, needed);
}
