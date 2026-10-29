import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Lets the Docker image run the slim standalone server (`node server.js`).
  output: "standalone",
};

export default nextConfig;
