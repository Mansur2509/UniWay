import type { Metadata } from "next";

import { ResetPasswordScreen } from "@/screens/auth";

export const metadata: Metadata = {
  title: "Reset password"
};

export default function Page() {
  return <ResetPasswordScreen />;
}
