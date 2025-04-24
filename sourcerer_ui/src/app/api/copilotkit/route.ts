// pages/api/copilotkit/route.ts OR app/api/copilotkit/route.ts

import {
  CopilotRuntime,
  OpenAIAdapter, // <-- Import the adapter
  copilotRuntimeNextJSAppRouterEndpoint,
  copilotKitEndpoint,
} from "@copilotkit/runtime";
import OpenAI from "openai"; // <-- Import OpenAI
import { NextRequest } from "next/server";

// --- Initialize OpenAI and the Adapter ---
// Ensure you have OPENAI_API_KEY in your .env file
const openai = new OpenAI(); // Assumes OPENAI_API_KEY is set in env vars
const llmAdapter = new OpenAIAdapter({ openai }); // Create adapter instance
// ------------------------------------------


export const POST = async (req: NextRequest) => {
  const remoteEndpoint = copilotKitEndpoint({
      url: process.env.REMOTE_ACTION_URL || "http://localhost:8000/copilotkit",
      // Optional: Consider adding agentConfigurations if needed
      // agentConfigurations: [{ agentId: "sourcerer_agent" }]
    });

  const runtime = new CopilotRuntime({
    remoteEndpoints: [remoteEndpoint],
  });

  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter: llmAdapter, // <-- Pass the adapter instance here
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};

// Optional: Add GET handler if needed
// export const GET = POST;