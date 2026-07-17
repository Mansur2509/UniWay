import type { Metadata } from "next";

import { ForgotPasswordScreen } from "@/screens/auth";

export const metadata: Metadata = {
  title: "Forgot password"
};

export default function Page() {
  return <ForgotPasswordScreen />;
}
