import type { Metadata } from "next";

import { RegisterScreen } from "@/screens/auth";

export const metadata: Metadata = {
  title: "Register"
};

export default function Page() {
  return <RegisterScreen />;
}

