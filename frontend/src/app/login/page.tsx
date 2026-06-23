import type { Metadata } from "next";

import { LoginScreen } from "@/screens/auth";

export const metadata: Metadata = {
  title: "Login"
};

export default function Page() {
  return <LoginScreen />;
}

