import { AuthForm } from "@/features/auth/ui/auth-form";

export function LoginScreen() {
  return (
    <div className="grid min-h-[calc(100vh-9rem)] place-items-center py-8">
      <AuthForm mode="login" />
    </div>
  );
}

export function RegisterScreen() {
  return (
    <div className="grid min-h-[calc(100vh-9rem)] place-items-center py-8">
      <AuthForm mode="register" />
    </div>
  );
}
