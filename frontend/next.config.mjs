/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // In production, NEXT_PUBLIC_API_URL should be set in Vercel env vars
    // In development, falls back to localhost:8000
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
