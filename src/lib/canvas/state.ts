import { AgentState, CardType, ChartData, EntityData, ItemData, NoteData, ProjectData } from "@/lib/canvas/types";

export const initialState: AgentState = {
  items: [],
  globalTitle: "",
  globalDescription: "",
  lastAction: "",
  itemsCreated: 0,
  planSteps: [],
  currentStepIndex: -1,
  planStatus: "",
};

export function isNonEmptyAgentState(value: unknown): value is AgentState {
  if (value == null || typeof value !== "object") return false;
  const v = value as Partial<AgentState> & Record<string, unknown>;
  const hasItems = Array.isArray(v.items) && v.items.length > 0;
  const hasPlan = Array.isArray(v.planSteps) && v.planSteps.length > 0;
  const hasTitle = typeof v.globalTitle === "string" && v.globalTitle.trim().length > 0;
  const hasDesc = typeof v.globalDescription === "string" && v.globalDescription.trim().length > 0;
  const hasCount = typeof v.itemsCreated === "number" && Number.isFinite(v.itemsCreated) && v.itemsCreated > 0;
  return hasItems || hasPlan || hasTitle || hasDesc || hasCount;
}

export function defaultDataFor(type: CardType): ItemData {
  switch (type) {
    case "project":
      return {
        field1: "",
        field2: "",
        field3: "",
        field4: [],
        field4_id: 0,
      } as ProjectData;
    case "entity":
      return {
        field1: "",
        field2: "",
        field3: [],
        field3_options: ["Tag 1", "Tag 2", "Tag 3"],
      } as EntityData;
    case "note":
      return { field1: "" } as NoteData;
    case "chart":
      return { field1: [], field1_id: 0 } as ChartData;
    default:
      return { field1: "" } as NoteData;
  }
}




