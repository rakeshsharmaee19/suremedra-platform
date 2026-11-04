/** @type {import('next').NextConfig} */
const API = process.env.API_INTERNAL_URL || "http://localhost:8000";

const nextConfig = {
  // Self-contained server build for Docker (copies only what is needed to run).
  output: "standalone",
  poweredByHeader: false,

  async rewrites() {
    // Local development: the browser calls /api/... on :3000 and Next forwards it to Django.
    // In production Caddy routes /api/* to Django directly, so this is never reached.
    return [{ source: "/api/:path*", destination: `${API}/api/:path*` }];
  },

  async redirects() {
    return [{ source: "/products", destination: "/catalogue", permanent: true }];
  },
};

export default nextConfig;
