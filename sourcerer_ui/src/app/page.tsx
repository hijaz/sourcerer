import { CopilotKit } from "@copilotkit/react-core";
import Main from "../components/Main";

export default function Home() {
  const runtimeUrl = "/api/copilotkit";
  return (
    <CopilotKit runtimeUrl={runtimeUrl} agent="sourcerer_agent">
      <Main />
    </CopilotKit>
  );
}
