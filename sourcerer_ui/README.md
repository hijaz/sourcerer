# Sourcerer UI

This is a CopilotKit-powered Next.js frontend for the Sourcerer agent.

## Getting Started

1. **Install dependencies:**
   ```sh
   npm install
   # or
   pnpm install
   ```

2. **Configure API endpoint:**
   - Copy `.env.example` to `.env.local`.
   - Set:
     ```
     NEXT_PUBLIC_COPILOTKIT_URL=http://localhost:8000/copilotkit
     ```

3. **Run the app:**
   ```sh
   npm run dev
   # or
   pnpm dev
   ```

4. **Open your browser:**
   - Go to [http://localhost:3000](http://localhost:3000)

## Features
- Chat with your Sourcerer
- Upload CSV bank statements
- View categorized transactions
- Real-time updates via CopilotKit

---

This UI is scaffolded from the CopilotKit Next.js example for quick integration with your backend agent.
