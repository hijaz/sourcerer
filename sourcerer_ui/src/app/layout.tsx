import type { Metadata } from "next";
import "@copilotkit/react-ui/styles.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sourcerer UI",
  description: "A Next.js CopilotKit Sourcerer UI",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
