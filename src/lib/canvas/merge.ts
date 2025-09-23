import type {
  AgentState,
  Item,
  ItemData,
  ProjectData,
  EntityData,
  NoteData,
  ChartData,
  ChartMetric,
} from "@/lib/canvas/types";

function preferNonEmptyString(incoming: unknown, cached: string): string {
  const s = typeof incoming === "string" ? incoming : undefined;
  return s && s.trim().length > 0 ? s : cached;
}

function isArrayOfObjectsWithKeys<T extends object>(val: unknown, keys: (keyof T)[]): val is T[] {
  if (!Array.isArray(val)) return false;
  return val.every((v) => {
    if (v == null || typeof v !== "object") return false;
    for (const k of keys) {
      if (!(k in (v as T))) return false;
    }
    return true;
  });
}

function mergeArrayById<T extends { id: string }>(
  cached: T[],
  incoming: T[],
  mergeItem: (prev: T, next: T) => T
): T[] {
  const byId = new Map<string, T>();
  for (const c of cached) byId.set(c.id, c);
  for (const n of incoming) {
    const prev = byId.get(n.id);
    byId.set(n.id, prev ? mergeItem(prev, n) : n);
  }
  // preserve cached order; append any new ids
  const result: T[] = [];
  const incomingIds = new Set(incoming.map((m) => m.id));
  for (const c of cached) result.push(byId.get(c.id)!);
  for (const n of incoming) {
    if (!incomingIds.has(n.id)) continue;
    if (!cached.some((c) => c.id === n.id)) result.push(byId.get(n.id)!);
  }
  return result;
}

function mergeProjectData(cached: ProjectData, incoming: ProjectData): ProjectData {
  const merged: ProjectData = {
    ...cached,
    field1: preferNonEmptyString(incoming.field1, cached.field1),
    field2: preferNonEmptyString(incoming.field2, cached.field2),
    field3: preferNonEmptyString(incoming.field3, cached.field3),
    field4: cached.field4,
    field4_id: Math.max(cached.field4_id ?? 0, incoming.field4_id ?? 0),
  };
  if (isArrayOfObjectsWithKeys(cached.field4, ["id", "text"]) || isArrayOfObjectsWithKeys(incoming.field4, ["id", "text"])) {
    const prev = Array.isArray(cached.field4) ? cached.field4 : [];
    const next = Array.isArray(incoming.field4) ? incoming.field4 : [];
    merged.field4 = mergeArrayById(prev, next, (a, b) => ({
      id: b.id,
      text: preferNonEmptyString((b as any).text, (a as any).text),
      done: typeof (b as any).done === "boolean" ? (b as any).done : (a as any).done,
      proposed: typeof (b as any).proposed === "boolean" ? (b as any).proposed : (a as any).proposed,
    } as any));
  }
  return merged;
}

function mergeEntityData(cached: EntityData, incoming: EntityData): EntityData {
  return {
    ...cached,
    field1: preferNonEmptyString(incoming.field1, cached.field1),
    field2: preferNonEmptyString(incoming.field2, cached.field2),
    field3: Array.isArray(incoming.field3) && incoming.field3.length > 0 ? incoming.field3 : cached.field3,
    field3_options: Array.isArray(incoming.field3_options) && incoming.field3_options.length > 0 ? incoming.field3_options : cached.field3_options,
  };
}

function mergeNoteData(cached: NoteData, incoming: NoteData): NoteData {
  return {
    ...cached,
    field1: preferNonEmptyString(incoming.field1, cached.field1 ?? ""),
  };
}

function isChartMetricArray(val: unknown): val is ChartMetric[] {
  if (!Array.isArray(val)) return false;
  return val.every((v) => v && typeof v === "object" && typeof (v as ChartMetric).id === "string");
}

function mergeChartData(cached: ChartData, incoming: ChartData): ChartData {
  const merged: ChartData = {
    ...cached,
    field1: cached.field1,
    field1_id: Math.max(cached.field1_id ?? 0, incoming.field1_id ?? 0),
  };
  if (isChartMetricArray(cached.field1) || isChartMetricArray(incoming.field1)) {
    const prev = Array.isArray(cached.field1) ? cached.field1 : [];
    const next = Array.isArray(incoming.field1) ? incoming.field1 : [];
    merged.field1 = mergeArrayById(prev, next, (a, b) => ({
      id: b.id,
      label: preferNonEmptyString(b.label, a.label),
      value: typeof b.value === "number" || b.value === "" ? b.value : a.value,
    }));
  }
  return merged;
}

function mergeItemData(prev: ItemData, incoming: ItemData, type: string): ItemData {
  switch (type) {
    case "project":
      return mergeProjectData(prev as ProjectData, incoming as ProjectData);
    case "entity":
      return mergeEntityData(prev as EntityData, incoming as EntityData);
    case "note":
      return mergeNoteData(prev as NoteData, incoming as NoteData);
    case "chart":
      return mergeChartData(prev as ChartData, incoming as ChartData);
    default:
      // Fallback: prefer non-empty primitives, keep arrays from incoming if non-empty
      const out: Record<string, unknown> = { ...prev };
      for (const [k, v] of Object.entries(incoming as Record<string, unknown>)) {
        if (typeof v === "string") {
          out[k] = preferNonEmptyString(v, String((out as Record<string, unknown>)[k] ?? ""));
        } else if (Array.isArray(v)) {
          out[k] = v.length > 0 ? v : (out[k] ?? []);
        } else if (typeof v === "number") {
          out[k] = v;
        } else if (v === "") {
          out[k] = v; // allow explicit clears
        }
      }
      return out as ItemData;
  }
}

function mergeItems(prev: Item[], incoming: Item[], lastAction: string): Item[] {
  const prevById = new Map(prev.map((i) => [i.id, i] as const));
  const incomingById = new Map(incoming.map((i) => [i.id, i] as const));
  const deletedMatch = /^deleted:(.+)$/.exec(String(lastAction || ""));
  const deletedId = deletedMatch ? deletedMatch[1] : "";

  const result: Item[] = [];
  for (const oldItem of prev) {
    if (oldItem.id === deletedId) continue;
    const inc = incomingById.get(oldItem.id)?.[1];
    if (!inc) {
      result.push(oldItem);
      continue;
    }
    result.push({
      id: oldItem.id,
      type: inc.type || oldItem.type,
      name: preferNonEmptyString(inc.name, oldItem.name),
      subtitle: preferNonEmptyString(inc.subtitle, oldItem.subtitle),
      data: mergeItemData(oldItem.data, inc.data, (inc.type || oldItem.type)),
    });
    incomingById.delete(oldItem.id);
  }
  for (const [, inc] of incomingById) result.push(inc);
  return result;
}

export function mergeAgentStateSnapshots(prev: AgentState, incoming: AgentState): AgentState {
  const incomingItems = Array.isArray(incoming.items) ? (incoming.items as Item[]) : [];
  const mergedItems = incomingItems.length > 0 ? mergeItems(prev.items, incomingItems, String(incoming.lastAction || prev.lastAction || "")) : prev.items;
  return {
    items: mergedItems,
    globalTitle: preferNonEmptyString(incoming.globalTitle, prev.globalTitle),
    globalDescription: preferNonEmptyString(incoming.globalDescription, prev.globalDescription),
    lastAction: preferNonEmptyString(incoming.lastAction, String(prev.lastAction || "")),
    itemsCreated: Math.max(
      Number.isFinite(incoming.itemsCreated as number) ? (incoming.itemsCreated as number) : 0,
      Number.isFinite(prev.itemsCreated as number) ? (prev.itemsCreated as number) : 0,
    ),
    // Always adopt incoming plan state to keep tracker up to date
    planSteps: Array.isArray(incoming.planSteps) ? incoming.planSteps : prev.planSteps,
    currentStepIndex: typeof incoming.currentStepIndex === "number" ? incoming.currentStepIndex : prev.currentStepIndex,
    planStatus: typeof incoming.planStatus === "string" ? incoming.planStatus : prev.planStatus,
  };
}


