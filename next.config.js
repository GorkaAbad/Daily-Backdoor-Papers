/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  basePath: '/backdoor-papers',
  assetPrefix: '/backdoor-papers/',
}

module.exports = nextConfig

