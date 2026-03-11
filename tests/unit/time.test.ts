import { describe, it, expect } from "vitest";
import {
  getCountdown,
  formatCountdown,
  getTodayName,
  WEEKDAYS,
} from "../../src/lib/time";

describe("getCountdown", () => {
  it("returns correct breakdown for a future date", () => {
    const now = new Date("2025-03-01T12:00:00Z");
    const target = "2025-03-02T14:30:45Z";
    const result = getCountdown(target, now);

    expect(result).not.toBeNull();
    expect(result!.days).toBe(1);
    expect(result!.hours).toBe(2);
    expect(result!.minutes).toBe(30);
    expect(result!.seconds).toBe(45);
  });

  it("returns null for a past date", () => {
    const now = new Date("2025-03-02T12:00:00Z");
    const target = "2025-03-01T12:00:00Z";
    expect(getCountdown(target, now)).toBeNull();
  });

  it("returns null for an invalid date string", () => {
    expect(getCountdown("not-a-date")).toBeNull();
  });

  it("returns null when target equals now", () => {
    const now = new Date("2025-03-01T12:00:00Z");
    expect(getCountdown("2025-03-01T12:00:00Z", now)).toBeNull();
  });

  it("handles large time differences", () => {
    const now = new Date("2025-01-01T00:00:00Z");
    const target = "2025-01-08T12:30:15Z";
    const result = getCountdown(target, now);

    expect(result).not.toBeNull();
    expect(result!.days).toBe(7);
    expect(result!.hours).toBe(12);
    expect(result!.minutes).toBe(30);
    expect(result!.seconds).toBe(15);
  });

  it("returns positive total_ms", () => {
    const now = new Date("2025-03-01T12:00:00Z");
    const result = getCountdown("2025-03-01T13:00:00Z", now);
    expect(result).not.toBeNull();
    expect(result!.total_ms).toBe(3600000);
  });
});

describe("formatCountdown", () => {
  it("formats full countdown", () => {
    const result = formatCountdown({
      days: 2,
      hours: 5,
      minutes: 30,
      seconds: 10,
      total_ms: 0,
    });
    expect(result).toBe("2d 5h 30m 10s");
  });

  it("omits zero days", () => {
    const result = formatCountdown({
      days: 0,
      hours: 3,
      minutes: 15,
      seconds: 0,
      total_ms: 0,
    });
    expect(result).toBe("3h 15m 0s");
  });

  it("shows only seconds when under a minute", () => {
    const result = formatCountdown({
      days: 0,
      hours: 0,
      minutes: 0,
      seconds: 45,
      total_ms: 0,
    });
    expect(result).toBe("45s");
  });

  it("omits zero hours and minutes", () => {
    const result = formatCountdown({
      days: 1,
      hours: 0,
      minutes: 0,
      seconds: 5,
      total_ms: 0,
    });
    expect(result).toBe("1d 5s");
  });
});

describe("getTodayName", () => {
  it("returns a valid weekday string", () => {
    const today = getTodayName();
    expect(WEEKDAYS).toContain(today);
  });
});

describe("WEEKDAYS", () => {
  it("has 7 entries starting from monday", () => {
    expect(WEEKDAYS).toHaveLength(7);
    expect(WEEKDAYS[0]).toBe("monday");
    expect(WEEKDAYS[6]).toBe("sunday");
  });
});
