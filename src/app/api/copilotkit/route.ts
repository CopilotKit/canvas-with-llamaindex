import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";
import { NextRequest } from "next/server";

// 1. You can use any service adapter here for multi-agent support. We use
//    the empty adapter since we're only using one agent.
const serviceAdapter = new ExperimentalEmptyAdapter();

// 2. Create the CopilotRuntime instance and utilize the LlamaIndex AG-UI
//    integration to setup the connection.
const runtime = new CopilotRuntime({
  agents: {
    // Our FastAPI endpoint URL
    sample_agent: new HttpAgent({
      debug: true,
      url: "http://127.0.0.1:9000/run",
    }),
  }
})

export async function POST(request: NextRequest) {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: `/api/copilotkit`,
  });

  return handleRequest(request);
}
