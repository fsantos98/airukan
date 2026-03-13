import { useState, useMemo } from "react";
import { getUserTimezone, setUserTimezone } from "../lib/timezone";

const COMMON_TIMEZONES = [
  "Pacific/Midway",
  "Pacific/Honolulu",
  "America/Anchorage",
  "America/Los_Angeles",
  "America/Denver",
  "America/Chicago",
  "America/New_York",
  "America/Sao_Paulo",
  "Atlantic/Azores",
  "Europe/London",
  "Europe/Lisbon",
  "Europe/Paris",
  "Europe/Berlin",
  "Europe/Helsinki",
  "Europe/Moscow",
  "Asia/Dubai",
  "Asia/Kolkata",
  "Asia/Bangkok",
  "Asia/Shanghai",
  "Asia/Tokyo",
  "Australia/Sydney",
  "Pacific/Auckland",
];

function getAllTimezones(): string[] {
  try {
    return Intl.supportedValuesOf("timeZone");
  } catch {
    return COMMON_TIMEZONES;
  }
}

export default function TimezoneSelector() {
  const [timezone, setTz] = useState(() => getUserTimezone());
  const [search, setSearch] = useState("");

  const allTimezones = useMemo(() => getAllTimezones(), []);

  const filtered = search
    ? allTimezones.filter((tz) =>
        tz.toLowerCase().includes(search.toLowerCase()),
      )
    : allTimezones;

  const handleChange = (newTz: string) => {
    setTz(newTz);
    setUserTimezone(newTz);
  };

  return (
    <div className="max-w-md">
      <label className="block text-sm font-medium text-text mb-2">
        Timezone
      </label>
      <p className="text-xs text-text-muted mb-4">
        Choose your timezone to see anime airing times and schedule organized
        for your local time.
      </p>
      <input
        type="text"
        placeholder="Search timezone..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full rounded-lg bg-surface border border-surface-lighter px-3 py-2 text-sm text-text placeholder:text-text-muted focus:border-primary focus:outline-none mb-2"
      />
      <select
        value={timezone}
        onChange={(e) => handleChange(e.target.value)}
        size={10}
        className="w-full rounded-lg bg-surface border border-surface-lighter px-3 py-2 text-sm text-text focus:border-primary focus:outline-none"
      >
        {filtered.map((tz) => (
          <option key={tz} value={tz}>
            {tz.replace(/_/g, " ")}
          </option>
        ))}
      </select>
      <p className="mt-3 text-sm text-text-muted">
        Current:{" "}
        <span className="text-primary-light font-medium">
          {timezone.replace(/_/g, " ")}
        </span>
      </p>
    </div>
  );
}
