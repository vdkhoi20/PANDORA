import BeforeAfterSlider from "./components/BeforeAfterSlider";
import HoverClickGallery from "./components/HoverClickGallery";
import InteractiveDemo from "./components/InteractiveDemo";
import QuantitativeTable from "./components/QuantitativeTable";
import fs from "fs";
import path from "path";
import { Pacifico } from "next/font/google";

const titleScript = Pacifico({
  subsets: ["latin"],
  weight: "400",
});

export default async function Home() {
  // Discover all result triplets in public/results at build/render time
  const resultsDir = path.join(process.cwd(), "public", "results");
  let galleryItems: { id: string; originalSrc: string; resultSrc: string; maskSrc: string }[] = [];
  try {
    const entries = await fs.promises.readdir(resultsDir);
    const tripletPresence: Record<string, { original: boolean; result: boolean; mask: boolean }> = {};

    const filenamePattern = /^img_(\d+)_(original|result|mask)\.png$/;
    for (const name of entries) {
      const match = name.match(filenamePattern);
      if (!match) continue;
      const index = match[1];
      const kind = match[2] as "original" | "result" | "mask";
      if (!tripletPresence[index]) {
        tripletPresence[index] = { original: false, result: false, mask: false };
      }
      tripletPresence[index][kind] = true;
    }

    const indices = Object.keys(tripletPresence)
      .filter((k) => {
        const t = tripletPresence[k];
        return t.original && t.result && t.mask;
      })
      .map((k) => Number(k))
      .sort((a, b) => a - b);

    galleryItems = indices.map((i) => ({
      id: String(i),
      originalSrc: `/results/img_${i}_original.png`,
      resultSrc: `/results/img_${i}_result.png`,
      maskSrc: `/results/img_${i}_mask.png`,
    }));
  } catch {
    galleryItems = [];
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-50 via-white to-sky-100 text-gray-900">
      {/* Hero Section */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto text-center">
          {/* Title */}
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-semibold leading-tight mb-8 px-4 flex flex-col items-center gap-3 text-center">
            <span className="flex flex-wrap items-center justify-center gap-3">
              <span
                className={`${titleScript.className} bg-clip-text text-transparent bg-gradient-to-r from-pink-400 via-purple-400 to-sky-400`}
              >
                PANDORA
              </span>
              <img
                src="/eraser.svg"
                alt="Eraser"
                className="w-10 h-10 md:w-12 md:h-12 lg:w-14 lg:h-14 inline-block drop-shadow-sm"
              />
            </span>
            <span className="text-xl md:text-2xl lg:text-3xl font-normal text-slate-700">
              Pixel-wise Attention Dissolution and Latent Guidance for Zero-Shot Object Removal
            </span>
          </h1>

          {/* Authors */}
          <div className="text-base md:text-lg mb-4 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sky-600">
            <span>
              <a
                href="https://orcid.org/0000-0001-8831-8846"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-sky-500 hover:underline font-medium"
              >
                Dinh-Khoi Vo
              </a>
              <sup className="ml-0.5 text-slate-500">1,2</sup>
            </span>
            <span>
              <a
                href="https://orcid.org/0000-0001-9351-3750"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-sky-500 hover:underline font-medium"
              >
                Van-Loc Nguyen
              </a>
              <sup className="ml-0.5 text-slate-500">1,2</sup>
            </span>
            <span>
              <a
                href="#"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-sky-500 hover:underline font-medium"
              >
                Tam V. Nguyen
              </a>
              <sup className="ml-0.5 text-slate-500">3</sup>
            </span>
            <span>
              <a
                href="https://orcid.org/0000-0003-3046-3041"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-sky-500 hover:underline font-medium"
              >
                Minh-Triet Tran
              </a>
              <sup className="ml-0.5 text-slate-500">1,2</sup>
            </span>
            <span>
              <a
                href="https://orcid.org/0000-0002-7363-2610"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-sky-500 hover:underline font-medium"
              >
                Trung-Nghia Le
              </a>
              <sup className="ml-0.5 text-slate-500">1,2</sup>
            </span>
          </div>

          {/* Affiliations */}
          <div className="text-xs md:text-sm lg:text-base mb-4 flex flex-col items-center justify-center gap-y-1 text-slate-600">
            <span>
              <sup className="mr-0.5">1</sup>University of Science, VNU-HCM, Ho Chi Minh City, Vietnam
            </span>
            <span>
              <sup className="mr-0.5">2</sup>Vietnam National University, Ho Chi Minh City, Vietnam
            </span>
            <span>
              <sup className="mr-0.5">3</sup>University of Dayton, Ohio, United States
            </span>
          </div>

          {/* Email */}
          <div className="text-xs md:text-sm lg:text-base mb-10 italic text-slate-500">
            &#123;vdkhoi, nvloc&#125;@selab.hcmus.edu.vn, tamnguyen@udayton.edu, &#123;tmtriet, ltnghia&#125;@fit.hcmus.edu.vn
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-4 md:gap-6 mb-14">
            <a
              href="/PANDORA.pdf"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-slate-900 text-white text-sm md:text-base font-medium shadow-sm hover:bg-slate-800 transition-colors"
              rel="noopener noreferrer"
            >
              <span className="text-lg">📄</span>
              <span>Paper PDF</span>
            </a>
            <a
              href="#"
              className="relative inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white text-slate-700 text-sm md:text-base font-medium border border-slate-200 shadow-sm cursor-not-allowed opacity-80"
              title="Coming soon"
            >
              <span className="text-lg">🧾</span>
              <span>arXiv</span>
              <span className="absolute -top-1 -right-1 bg-rose-500 text-white text-[10px] px-1.5 py-0.5 rounded-full font-semibold tracking-wide">
                SOON
              </span>
            </a>
            <a
              href="#"
              className="relative inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white text-slate-700 text-sm md:text-base font-medium border border-slate-200 shadow-sm cursor-not-allowed opacity-80"
              title="Coming soon"
            >
              <span className="text-lg">💻</span>
              <span>Code</span>
              <span className="absolute -top-1 -right-1 bg-rose-500 text-white text-[10px] px-1.5 py-0.5 rounded-full font-semibold tracking-wide">
                SOON
              </span>
            </a>
            <a
              href="https://4e5fb5a771209acf2f.gradio.live/"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-emerald-500 text-white text-sm md:text-base font-medium shadow-sm hover:bg-emerald-600 transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              <span className="text-lg">🚀</span>
              <span>Gradio Demo</span>
            </a>
            <a
              href="https://docs.google.com/forms/d/e/1FAIpQLSf6j6FOHiCdcZJJJ5DVRVgFTxIPTzEH91o2XVbsFNU6Xpp9Ig/viewform"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white text-slate-700 text-sm md:text-base font-medium border border-slate-200 shadow-sm hover:bg-slate-50 transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              <span className="text-lg">💬</span>
              <span>Feedback</span>
            </a>
          </div>

          {/* Hero Video Demo */}
          <div className="max-w-4xl mx-auto bg-white/80 border border-slate-100 rounded-3xl p-6 md:p-8 shadow-sm">
            <h2 className="text-2xl md:text-3xl text-slate-800 font-semibold mb-4 md:mb-6">
              Demo Video
            </h2>
            <div className="aspect-video bg-slate-900 rounded-2xl overflow-hidden relative shadow-md">
              <video
                className="w-full h-full object-cover"
                controls
                loop
                muted
                playsInline
              >
                <source src="/demo_video.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </video>
              {/* Video Labels */}
              <div className="absolute top-4 left-4 bg-black/60 backdrop-blur px-3 py-1 rounded-full text-xs md:text-sm font-medium text-white">
                Original
              </div>
              <div className="absolute top-4 right-4 bg-black/60 backdrop-blur px-3 py-1 rounded-full text-xs md:text-sm font-medium text-white">
                Result
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Abstract Section */}
      <section className="py-12 px-4 bg-gray-100 text-gray-900">
        <div className="max-w-6xl mx-auto">
          <div className="flex gap-8">
            <h2 className="text-3xl font-bold uppercase min-w-fit">Abstract</h2>
            <p className="text-lg leading-relaxed">
              Removing objects from natural images remains a formidable challenge, often hindered by the inability to synthesize semantically appropriate content in the foreground while preserving background integrity. Existing methods often rely on fine-tuning, prompt engineering, or inference-time optimization, yet still struggle to maintain texture consistency, produce rigid or unnatural results, lack precise foreground-background disentanglement, and fail to flexibly handle multiple objects—ultimately limiting their scalability and practical applicability. In this paper, we propose a zero-shot object removal framework that operates directly on pre-trained text-to-image diffusion models—requiring no fine-tuning, no prompts, and no optimization. At the core is our Pixel-wise Attention Dissolution, which performs fine-grained, pixel-wise dissolution of object information by nullifying the most correlated keys for each masked pixel. This operation causes the object to vanish from the self-attention flow, allowing the coherent background context to seamlessly dominate the reconstruction. To complement this, we introduce Localized Attentional Disentanglement Guidance, which steers the denoising process toward latent manifolds that favor clean object removal. Together, Pixel-wise Attention Dissolution and Localized Attentional Disentanglement Guidance enable precise, non-rigid, scalable, and prompt-free multi-object erasure in a single pass. Experiments show our method outperforms state-of-the-art methods even with fine-tuned and prompt-guided baselines in both visual fidelity and semantic plausibility.
            </p>
          </div>
        </div>
      </section>

      {/* Object Removal Section */}
      <section className="py-16 px-4 bg-white text-gray-900">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold uppercase text-center mb-6">Object Removal</h2>
          <p className="text-lg text-center max-w-4xl mx-auto leading-relaxed">
            We propose a zero-shot object removal framework that operates directly on pre-trained diffusion models in a single pass, without any fine-tuning, prompt engineering, or inference-time optimization, thus fully leveraging their latent generative capacity for inpainting
          </p>

          {/* Info Box */}
          {/* <div className="bg-blue-50 border border-blue-200 rounded-lg py-4 px-6 mb-8 text-center">
            <p className="text-blue-900 flex items-center justify-center gap-2">
              <span className="text-2xl">👆</span>
              <span>Slide any image to see results</span>
            </p>
          </div> */}

          {/* Image Gallery Grid */}
          {/* <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <BeforeAfterSlider beforeSrc="/results/img_1_original.png" afterSrc="/results/img_1_result.png" label="" />
            <BeforeAfterSlider beforeSrc="/results/img_2_original.png" afterSrc="/results/img_2_result.png" label="" />
            <BeforeAfterSlider beforeSrc="/results/img_3_original.png" afterSrc="/results/img_3_result.png" label="" />
            <BeforeAfterSlider beforeSrc="/results/img_4_original.png" afterSrc="/results/img_4_result.png" label="" />
            <BeforeAfterSlider beforeSrc="/results/img_5_original.png" afterSrc="/results/img_5_result.png" label="" />
            <BeforeAfterSlider beforeSrc="/results/img_6_original.png" afterSrc="/results/img_6_result.png" label="" />
            <BeforeAfterSlider beforeSrc="/results/img_7_original.png" afterSrc="/results/img_7_result.png" label="" />
            <BeforeAfterSlider beforeSrc="/results/img_8_original.png" afterSrc="/results/img_8_result.png" label="" />
          </div> */}
        </div>
      </section>

      {/* Interactive Gallery Section */}
      <section className="pt-2 pb-16 px-4 bg-gray-50 text-gray-900">
        <div className="max-w-6xl mx-auto">
          {/* <h2 className="text-3xl font-bold uppercase text-center mb-6">Interactive Results</h2>
          <p className="text-lg text-center mb-6 max-w-4xl mx-auto leading-relaxed">
            Hover over any image to see the object that will be removed, and click to toggle between original and result
          </p> */}

          {/* Info Box */}
          <div className="bg-green-50 border border-green-200 rounded-lg py-4 px-6 mb-8 text-center">
            <p className="text-green-900 flex items-center justify-center gap-2">
              <span className="text-2xl">🖱️</span>
              <span>Click to see results</span>
            </p>
            <p className="text-green-700 text-sm mt-2 flex items-center justify-center gap-2">
              <span className="text-lg">⏱️</span>
              <span>Processing takes ~10 seconds - please be patient!</span>
            </p>
          </div>

          {/* Interactive Gallery */}
          <HoverClickGallery items={galleryItems} />
        </div>
      </section>

      {/* Approach Section */}
      <section className="py-16 px-4 bg-gray-100 text-gray-900">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold uppercase text-center mb-6">Approach</h2>
          <div>
            <p className="text-lg leading-relaxed mb-6">
              Our framework performs zero-shot object removal directly on a pre-trained diffusion model. Given an input image <i>I<sub>s</sub></i> and a binary mask <i>M</i> specifying the target objects, the model produces an edited image <i>I<sub>t</sub></i> where the masked regions are erased and seamlessly reconstructed with contextually consistent background. The process begins with latent inversion to map the input image into the noise space while preserving unaffected regions in the denoising process. We then apply <strong>Pixel-wise Attention Dissolution (PAD)</strong> to disconnect masked query pixels from their most correlated keys, effectively dissolving object information at the attention level. Next, <strong>Localized Attentional Disentanglement Guidance (LADG)</strong> steers the denoising trajectory in latent space away from the object regions, refining the reconstruction to suppress residual artifacts.
            </p>
            <p className="text-lg leading-relaxed mb-6">
              Together, PAD and LADG enable precise, pixel-level control for single- and multi-object removal in a single forward pass, without any fine-tuning, prompt engineering, or inference-time optimization.
            </p>

            {/* Approach Diagram */}
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <img
                src="/pipeline.png"
                alt="PANDORA Pipeline Diagram"
                className="w-full h-auto rounded"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Qualitative Comparison Section */}
      <section className="py-16 px-4 bg-white text-gray-900">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold uppercase text-center mb-6">Qualitative Comparison</h2>

          {/* Enhanced Caption with Icons */}
          <div className="max-w-5xl mx-auto mb-8">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
              <p className="text-lg text-center mb-4 text-blue-900">
                <span className="flex items-center justify-center gap-2 mb-2">
                  <span className="text-2xl">🔬</span>
                  <span className="font-semibold">Qualitative comparison on various object removal scenarios</span>
                </span>
                <span className="flex items-center justify-center gap-2 text-base">
                  <span className="text-xl">📊</span>
                  <span>From left to right: original image with a mask, and results from different methods</span>
                </span>
              </p>
            </div>

            {/* Scenario Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                <div className="text-2xl mb-2">🎯</div>
                <h3 className="font-semibold text-green-900 mb-1">Single-Object Removal</h3>
                <p className="text-sm text-green-700">Top two rows</p>
              </div>
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
                <div className="text-2xl mb-2">🎯🎯</div>
                <h3 className="font-semibold text-orange-900 mb-1">Multi-Object Cases</h3>
                <p className="text-sm text-orange-700">Middle two rows</p>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
                <div className="text-2xl mb-2">🎯🎯🎯</div>
                <h3 className="font-semibold text-purple-900 mb-1">Mass-Similar Objects</h3>
                <p className="text-sm text-purple-700">Bottom two rows</p>
              </div>
            </div>

            {/* Zero-shot Methods Highlight */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-gray-800">
                <span className="text-xl mr-2">⚡</span>
                <span className="font-semibold">Zero-shot methods</span> shown in the last four columns, with the <span className="font-bold text-blue-600">last two columns showing our PANDORA method</span>
              </p>
            </div>
          </div>

          {/* Qualitative Comparison Image */}
          <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
            <img
              src="/qualitative.png"
              alt="Qualitative comparison of object removal methods"
              className="w-full h-auto rounded shadow-lg"
            />
          </div>
        </div>
      </section>

      {/* Quantitative Comparison Section */}
      <section className="py-16 px-4 bg-gray-50 text-gray-900">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold uppercase text-center mb-6">Quantitative Comparison</h2>
          <div className="bg-white rounded-lg p-6 border border-gray-200">
            <QuantitativeTable />
          </div>
        </div>
      </section>

      {/* BibTeX Section - Commented for now
      <section className="py-16 px-4 bg-white text-gray-900">
        <div className="max-w-6xl mx-auto">
          <div className="flex gap-8">
            <h2 className="text-3xl font-bold uppercase min-w-fit">BibTex</h2>
            <div className="flex-1">
              <pre className="bg-gray-50 border border-gray-200 rounded-lg p-6 overflow-x-auto text-sm font-mono">
{`@misc{winter2024objectdrop,
      title={ObjectDrop: Bootstrapping Counterfactuals for Photorealistic Object Removal and Insertion},
      author={Daniel Winter and Matan Cohen and Shlomi Fruchter and Yael Pritch and Alex Rav-Acha and Yedid Hoshen},
      year={2024},
      eprint={2403.18818},
      archivePrefix={arXiv},
      primaryClass={cs.CV}
}`}
              </pre>
            </div>
          </div>
        </div>
      </section>
      */}

      {/* Acknowledgment Section */}
      <section className="py-16 px-4 bg-gray-200 text-gray-900">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold uppercase text-center mb-6">Acknowledgment</h2>
          <div className="flex-1">
            {/* Funding and GPU Support */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 mb-6">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">💰</span>
                <h3 className="text-xl font-semibold text-amber-900">Funding and GPU Support</h3>
              </div>
              <p className="text-lg leading-relaxed text-amber-800">
                This research is funded by the Vietnam National Foundation for Science and Technology Development (NAFOSTED) under Grant Number 102.05-2023.31. This research used the GPUs provided by the Intelligent Systems Lab at the Faculty of Information Technology, University of Science, VNU-HCM.
              </p>
            </div>

            {/* User Study Participants */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">🙏</span>
                <h3 className="text-xl font-semibold text-blue-900">User Study Participants</h3>
              </div>
              <p className="text-lg leading-relaxed text-blue-800">
                We extend our heartfelt gratitude to all participants who took part in our comprehensive user study. Your valuable time, thoughtful feedback, and detailed evaluations were instrumental in validating the effectiveness and usability of our PANDORA framework. Your insights helped us understand the practical impact of our zero-shot object removal approach and provided crucial evidence of its superiority over existing methods.
              </p>
            </div>

            {/* Website Design Credit */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">🎨</span>
                <h3 className="text-xl font-semibold text-green-900">Website Design Inspiration</h3>
              </div>
              <p className="text-lg leading-relaxed text-green-800">
                This website design is inspired by{" "}
                <a
                  href="https://objectdrop.github.io/"
                  className="text-blue-600 hover:underline font-semibold"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  ObjectDrop
                </a>. We thank the authors for their excellent work and creative design approach.
              </p>
            </div>

            {/* Demo Design Credit */}
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">🚀</span>
                <h3 className="text-xl font-semibold text-purple-900">Demo Design Inspiration</h3>
              </div>
              <p className="text-lg leading-relaxed text-purple-800">
                Our Gradio demo design is inspired by{" "}
                <a
                  href="https://huggingface.co/spaces/xichenhku/MimicBrush/tree/main"
                  className="text-blue-600 hover:underline font-semibold"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  MimicBrush
                </a>. We thank the authors for their excellent work and creative design approach.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
