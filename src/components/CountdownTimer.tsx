import { useState, useEffect } from "react";
import { getCountdown, formatCountdown } from "../lib/time";

interface Props {
  nextAirUtc: string;
}

/** Live countdown timer — the only client-side JS component. */
export default function CountdownTimer({ nextAirUtc }: Props) {
  const [label, setLabel] = useState(() => {
    const cd = getCountdown(nextAirUtc);
    return cd ? formatCountdown(cd) : "Aired";
  });

  useEffect(() => {
    const tick = () => {
      const cd = getCountdown(nextAirUtc);
      setLabel(cd ? formatCountdown(cd) : "Aired");
    };

    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [nextAirUtc]);

  return (
    <time
      dateTime={nextAirUtc}
      className="rounded-lg bg-surface px-3 py-1 text-sm font-mono font-semibold text-countdown"
      data-testid="countdown"
    >
      {label}
    </time>
  );
}
