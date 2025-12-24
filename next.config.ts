/** @type {import('next').NextConfig} */

const isProd = process.env.NODE_ENV === 'production';
const repoName = 'PANDORA';

const nextConfig = {
  output: 'export',
  basePath: isProd ? `/${repoName}` : '',
  assetPrefix: isProd ? `/${repoName}/` : '',
  images: {
    unoptimized: true,
  },
  // Thêm dòng này để dùng biến global trong code React
  env: {
    NEXT_PUBLIC_BASE_PATH: isProd ? `/${repoName}` : '',
  },
};

module.exports = nextConfig;