/** @type {import('next').NextConfig} */

const isProd = process.env.NODE_ENV === 'production';
const repoName = 'PANDORA'; // Tên chính xác repo của bạn

const nextConfig = {
  output: 'export',
  
  // Quan trọng: Thêm tên repo vào đường dẫn khi chạy production (build)
  // Nếu đang chạy local (npm run dev) thì không cần
  basePath: isProd ? `/${repoName}` : '',
  assetPrefix: isProd ? `/${repoName}/` : '',

  images: {
    unoptimized: true,
  },
};

module.exports = nextConfig;