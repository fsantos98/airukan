/** Breakdown of remaining time until an event. */
export interface Countdown {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  total_ms: number;
}

/**
 * Compute the remaining time between now and a target ISO 8601 datetime.
 * Returns null if the target is in the past or invalid.
 */
export function getCountdown(targetUtc: string, now?: Date): Countdown | null {
  const target = new Date(targetUtc);
  if (isNaN(target.getTime())) {
    return null;
  }

  const current = now ?? new Date();
  const diff = target.getTime() - current.getTime();

  if (diff <= 0) {
    return null;
  }

  const totalSeconds = Math.floor(diff / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  return { days, hours, minutes, seconds, total_ms: diff };
}

/** Days of the week in order, starting from Monday. */
export const WEEKDAYS = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
] as const;

/**
 * Get the current day of the week as a lowercase string.
 * Uses the user's local timezone.
 */
export function getTodayName(): (typeof WEEKDAYS)[number] {
  const jsDay = new Date().getDay(); // 0=Sunday
  const idx = jsDay === 0 ? 6 : jsDay - 1; // shift to 0=Monday
  return WEEKDAYS[idx];
}

/**
 * Format a countdown object as a human-readable string.
 * Example: "2d 5h 30m 10s"
 */
export function formatCountdown(cd: Countdown): string {
  const parts: string[] = [];
  if (cd.days > 0) parts.push(`${cd.days}d`);
  if (cd.hours > 0) parts.push(`${cd.hours}h`);
  if (cd.minutes > 0) parts.push(`${cd.minutes}m`);
  parts.push(`${cd.seconds}s`);
  return parts.join(" ");
}
