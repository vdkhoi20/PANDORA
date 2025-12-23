import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "PANDORA: Pixel-wise Attention Dissolution and Latent Guidance for Zero-Shot Object Removal",
  description:
    "PANDORA: A zero-shot object removal framework that operates directly on pre-trained diffusion models using Pixel-wise Attention Dissolution and Localized Attentional Disentanglement Guidance.",
  icons: {
    icon: "/eraser.svg",
    shortcut: "/eraser.svg",
    apple: "/eraser.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
