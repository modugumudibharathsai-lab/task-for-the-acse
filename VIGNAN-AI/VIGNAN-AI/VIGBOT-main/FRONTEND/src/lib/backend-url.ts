/**
 * Normalized backend URL helper for VIGBOT.
 * Works seamlessly whether NEXT_PUBLIC_BACKEND_URL is set with or without /api/v1,
 * or even if unset on Vercel (defaults to live production Render API).
 */
export function getBackendUrl(): string {
  const envUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  let base = (envUrl && envUrl.trim().length > 0) ? envUrl.trim() : "https://vigbot-api.onrender.com";
  base = base.replace(/\/+$/, "");
  if (!base.endsWith("/api/v1")) {
    base += "/api/v1";
  }
  return base;
}

