import type { Schedule, LastUpdated } from "./types";
import fs from "node:fs";
import path from "node:path";

const DATA_DIR = path.resolve(process.cwd(), "data");

/** Load and parse the weekly schedule from data/schedule.json. */
export function loadSchedule(): Schedule {
  const filePath = path.join(DATA_DIR, "schedule.json");
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as Schedule;
}

/** Load and parse pipeline metadata from data/last_updated.json. */
export function loadLastUpdated(): LastUpdated {
  const filePath = path.join(DATA_DIR, "last_updated.json");
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as LastUpdated;
}
