from typing import Annotated, List, Optional, Dict, Any

from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI
from llama_index.protocols.ag_ui.events import StateSnapshotWorkflowEvent
from llama_index.protocols.ag_ui.router import get_ag_ui_workflow_router


# --- Frontend tool stubs (names/signatures only; execution happens in the UI) ---

def createItem(
    type: Annotated[str, "One of: project, entity, note, chart."],
    name: Annotated[Optional[str], "Optional item name."] = None,
) -> str:
    """Create a new canvas item and return its id."""
    return f"createItem({type}, {name})"

def deleteItem(
    itemId: Annotated[str, "Target item id."],
) -> str:
    """Delete an item by id."""
    return f"deleteItem({itemId})"

def setItemName(
    name: Annotated[str, "New item name/title."],
    itemId: Annotated[str, "Target item id."],
) -> str:
    """Set an item's name."""
    return f"setItemName(name, {itemId})"

def setItemSubtitleOrDescription(
    subtitle: Annotated[str, "Item subtitle/short description."],
    itemId: Annotated[str, "Target item id."],
) -> str:
    """Set an item's subtitle/description (not data fields)."""
    return f"setItemSubtitleOrDescription({subtitle}, {itemId})"

def setGlobalTitle(title: Annotated[str, "New global title."]) -> str:
    """Set the global canvas title."""
    return f"setGlobalTitle({title})"

def setGlobalDescription(description: Annotated[str, "New global description."]) -> str:
    """Set the global canvas description."""
    return f"setGlobalDescription({description})"

# Note actions
def setNoteField1(
    value: Annotated[str, "New content for note.data.field1."],
    itemId: Annotated[str, "Target note id."],
) -> str:
    return f"setNoteField1({value}, {itemId})"

def appendNoteField1(
    value: Annotated[str, "Text to append to note.data.field1."],
    itemId: Annotated[str, "Target note id."],
    withNewline: Annotated[Optional[bool], "Prefix with newline if true." ] = None,
) -> str:
    return f"appendNoteField1({value}, {itemId}, {withNewline})"

def clearNoteField1(
    itemId: Annotated[str, "Target note id."],
) -> str:
    return f"clearNoteField1({itemId})"

# Project actions
def setProjectField1(value: Annotated[str, "New value for project.data.field1."], itemId: Annotated[str, "Project id."]) -> str:
    return f"setProjectField1({value}, {itemId})"

def setProjectField2(value: Annotated[str, "New value for project.data.field2."], itemId: Annotated[str, "Project id."]) -> str:
    return f"setProjectField2({value}, {itemId})"

def setProjectField3(date: Annotated[str, "Date YYYY-MM-DD for project.data.field3."], itemId: Annotated[str, "Project id."]) -> str:
    return f"setProjectField3({date}, {itemId})"

def clearProjectField3(itemId: Annotated[str, "Project id."]) -> str:
    return f"clearProjectField3({itemId})"

def addProjectChecklistItem(
    itemId: Annotated[str, "Project id."],
    text: Annotated[Optional[str], "Checklist text."] = None,
) -> str:
    return f"addProjectChecklistItem({itemId}, {text})"

def setProjectChecklistItem(
    itemId: Annotated[str, "Project id."],
    checklistItemId: Annotated[str, "Checklist item id or index."],
    text: Annotated[Optional[str], "New text."] = None,
    done: Annotated[Optional[bool], "New done status."] = None,
) -> str:
    return f"setProjectChecklistItem({itemId}, {checklistItemId}, {text}, {done})"

def removeProjectChecklistItem(
    itemId: Annotated[str, "Project id."],
    checklistItemId: Annotated[str, "Checklist item id."],
) -> str:
    return f"removeProjectChecklistItem({itemId}, {checklistItemId})"

# Entity actions
def setEntityField1(value: Annotated[str, "New value for entity.data.field1."], itemId: Annotated[str, "Entity id."]) -> str:
    return f"setEntityField1({value}, {itemId})"

def setEntityField2(value: Annotated[str, "New value for entity.data.field2."], itemId: Annotated[str, "Entity id."]) -> str:
    return f"setEntityField2({value}, {itemId})"

def addEntityField3(tag: Annotated[str, "Tag to add."], itemId: Annotated[str, "Entity id."]) -> str:
    return f"addEntityField3({tag}, {itemId})"

def removeEntityField3(tag: Annotated[str, "Tag to remove."], itemId: Annotated[str, "Entity id."]) -> str:
    return f"removeEntityField3({tag}, {itemId})"

# Chart actions
def addChartField1(
    itemId: Annotated[str, "Chart id."],
    label: Annotated[Optional[str], "Metric label."] = None,
    value: Annotated[Optional[float], "Metric value 0..100."] = None,
) -> str:
    return f"addChartField1({itemId}, {label}, {value})"

def setChartField1Label(itemId: Annotated[str, "Chart id."], index: Annotated[int, "Metric index (0-based)."], label: Annotated[str, "New metric label."]) -> str:
    return f"setChartField1Label({itemId}, {index}, {label})"

def setChartField1Value(itemId: Annotated[str, "Chart id."], index: Annotated[int, "Metric index (0-based)."], value: Annotated[float, "Value 0..100."]) -> str:
    return f"setChartField1Value({itemId}, {index}, {value})"

def clearChartField1Value(itemId: Annotated[str, "Chart id."], index: Annotated[int, "Metric index (0-based)."]) -> str:
    return f"clearChartField1Value({itemId}, {index})"

def removeChartField1(itemId: Annotated[str, "Chart id."], index: Annotated[int, "Metric index (0-based)."]) -> str:
    return f"removeChartField1({itemId}, {index})"

# --- Backend tools (server-side) ---

async def set_plan(
    ctx: Context,
    steps: Annotated[List[str], "Step titles to initialize a plan with."],
) -> Dict[str, Any]:
    """Initialize a plan consisting of step descriptions. Resets progress and sets status to 'in_progress'."""
    state: Dict[str, Any] = await ctx.get("state", default={})
    plan_steps = [{"title": str(s), "status": "pending"} for s in (steps or [])]
    if plan_steps:
        plan_steps[0]["status"] = "in_progress"
        state["currentStepIndex"] = 0
        state["planStatus"] = "in_progress"
    else:
        state["currentStepIndex"] = -1
        state["planStatus"] = ""
    state["planSteps"] = plan_steps
    ctx.write_event_to_stream(StateSnapshotWorkflowEvent(snapshot=state))
    await ctx.set(state)
    return {"initialized": True, "steps": steps}


async def update_plan_progress(
    ctx: Context,
    step_index: Annotated[int, "Index of the step to update (0-based)."],
    status: Annotated[str, "One of: pending, in_progress, completed, blocked, failed"],
    note: Annotated[Optional[str], "Optional short note for this step."] = None,
) -> Dict[str, Any]:
    """Update a single plan step's status, and optionally add a note."""
    state: Dict[str, Any] = await ctx.get("state", default={})
    steps: List[Dict[str, Any]] = list(state.get("planSteps", []) or [])
    if 0 <= step_index < len(steps):
        if note:
            steps[step_index]["note"] = note
        steps[step_index]["status"] = status
        state["planSteps"] = steps
        # current index & overall status heuristics
        if status == "in_progress":
            state["currentStepIndex"] = step_index
            state["planStatus"] = "in_progress"
        # Aggregate overall status
        statuses = [str(s.get("status", "")) for s in steps]
        if any(s == "failed" for s in statuses):
            state["planStatus"] = "failed"
        elif any(s == "in_progress" for s in statuses):
            state["planStatus"] = "in_progress"
        elif all(s == "completed" for s in statuses) and steps:
            state["planStatus"] = "completed"
            state["currentStepIndex"] = max(0, len(steps) - 1)
        else:
            # leave as-is
            pass
        ctx.write_event_to_stream(StateSnapshotWorkflowEvent(snapshot=state))
        await ctx.set(state)
        return {"updated": True, "index": step_index, "status": status, "note": note}
    return {"updated": False, "index": step_index, "status": status, "note": note}


async def complete_plan(ctx: Context) -> Dict[str, Any]:
    """Mark the plan as completed."""
    state: Dict[str, Any] = await ctx.get("state", default={})
    steps: List[Dict[str, Any]] = list(state.get("planSteps", []) or [])
    for s in steps:
        s["status"] = "completed"
    state["planSteps"] = steps
    state["planStatus"] = "completed"
    state["currentStepIndex"] = max(0, len(steps) - 1) if steps else -1
    ctx.write_event_to_stream(StateSnapshotWorkflowEvent(snapshot=state))
    await ctx.set(state)
    return {"completed": True}


FIELD_SCHEMA = (
    "FIELD SCHEMA (authoritative):\n"
    "- project.data:\n"
    "  - field1: string (text)\n"
    "  - field2: string (select: 'Option A' | 'Option B' | 'Option C')\n"
    "  - field3: string (date 'YYYY-MM-DD')\n"
    "  - field4: ChecklistItem[] where ChecklistItem={id: string, text: string, done: boolean, proposed: boolean}\n"
    "- entity.data:\n"
    "  - field1: string\n"
    "  - field2: string (select: 'Option A' | 'Option B' | 'Option C')\n"
    "  - field3: string[] (selected tags; subset of field3_options)\n"
    "  - field3_options: string[] (available tags)\n"
    "- note.data:\n"
    "  - field1: string (textarea; represents description)\n"
    "- chart.data:\n"
    "  - field1: Array<{id: string, label: string, value: number | ''}> with value in [0..100] or ''\n"
)

SYSTEM_PROMPT = (
    "You are a helpful AG-UI assistant.\n\n"
    + FIELD_SCHEMA +
    "\nMUTATION/TOOL POLICY:\n"
    "- When you claim to create/update/delete, you MUST call the corresponding tool(s) (frontend or backend).\n"
    "- To create new cards, call the frontend tool `createItem` with `type` in {project, entity, note, chart} and optional `name`.\n"
    "- After tools run, rely on the latest shared state (ground truth) when replying.\n"
    "- To set a card's subtitle (never the data fields): use setItemSubtitleOrDescription.\n\n"
    "DESCRIPTION MAPPING:\n"
    "- For project/entity/chart: treat 'description', 'overview', 'summary', 'caption', 'blurb' as the card subtitle; use setItemSubtitleOrDescription.\n"
    "- For notes: 'content', 'description', 'text', or 'note' refers to note content; use setNoteField1 / appendNoteField1 / clearNoteField1.\n\n"
    "PLANNING POLICY:\n"
    "- MANDATORY: If the user's request includes more than one action or involves creating/updating multiple items, FIRST propose a short plan (2-6 steps) and call set_plan with the step titles BEFORE any other tool calls.\n"
    "- For each step, call update_plan_progress to mark in_progress and then completed/failed with a short note.\n"
    "- When all steps are done, call complete_plan and provide a concise summary.\n\n"
    "DO NOT merely describe a plan in chat. You MUST call the plan tools (set_plan, update_plan_progress, complete_plan) to update the shared plan state so the UI can render progress. If tool calls fail, retry once with corrected arguments; otherwise report the error briefly and stop.\n\n"
    "ID POLICY:\n"
    "- Treat values like '0001', '0002', etc. as internal item identifiers produced by tools.\n"
    "- Do NOT interpret these IDs as user input and do not ask the user what to do with them unless the user explicitly mentions them.\n"
    "- When creating items, use the returned IDs directly in subsequent tool calls without calling attention to them in chat.\n\n"
    "STRICT GROUNDING RULES:\n"
    "1) ONLY use shared state (items/globalTitle/globalDescription/plan*) as the source of truth.\n"
    "2) Before ANY read or write, assume values may have changed; always read the latest state.\n"
    "3) If a command doesn't specify which item to change, ask to clarify.\n"
)

agentic_chat_router = get_ag_ui_workflow_router(
    llm=OpenAI(model="gpt-4.1"),
    # Provide frontend tool stubs so the model knows their names/signatures.
    frontend_tools=[
        createItem,
        deleteItem,
        setItemName,
        setItemSubtitleOrDescription,
        setGlobalTitle,
        setGlobalDescription,
        setNoteField1,
        appendNoteField1,
        clearNoteField1,
        setProjectField1,
        setProjectField2,
        setProjectField3,
        clearProjectField3,
        addProjectChecklistItem,
        setProjectChecklistItem,
        removeProjectChecklistItem,
        setEntityField1,
        setEntityField2,
        addEntityField3,
        removeEntityField3,
        addChartField1,
        setChartField1Label,
        setChartField1Value,
        clearChartField1Value,
        removeChartField1,
    ],
    backend_tools=[set_plan, update_plan_progress, complete_plan],
    system_prompt=SYSTEM_PROMPT,
    initial_state={
        # Shared state synchronized with the frontend canvas
        "items": [],
        "globalTitle": "",
        "globalDescription": "",
        "lastAction": "",
        "itemsCreated": 0,
        "planSteps": [],
        "currentStepIndex": -1,
        "planStatus": "",
    },
)
