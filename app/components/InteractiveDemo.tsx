"use client";

import Image from "next/image";
import { useRef, useState } from "react";

type DemoItem = {
    id: string;
    title: string;
    thumbSrc: string;
    videoSrc: string;
};

type InteractiveDemoProps = {
    items: DemoItem[];
    className?: string;
};

export default function InteractiveDemo({ items, className }: InteractiveDemoProps) {
    const [activeId, setActiveId] = useState(items[0]?.id);
    const videoRefs = useRef<Record<string, HTMLVideoElement | null>>({});

    const handleSelect = (id: string) => {
        // Pause others
        Object.entries(videoRefs.current).forEach(([key, vid]) => {
            if (key !== id && vid) {
                vid.pause();
                vid.currentTime = 0;
            }
        });
        setActiveId(id);
        const vid = videoRefs.current[id];
        // Play when switching
        if (vid) {
            void vid.play();
        }
    };

    const activeItem = items.find((i) => i.id === activeId) ?? items[0];

    return (
        <section className={className}>
            <h2 className="text-2xl font-semibold text-center">ObjectClear Interaction Demo</h2>

            {/* Thumbnails row */}
            <div className="mt-6 flex items-center justify-center gap-6">
                {items.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => handleSelect(item.id)}
                        className={`relative rounded-md ring-1 ring-zinc-200 dark:ring-zinc-800 overflow-hidden hover:shadow-md transition ${activeId === item.id ? "outline outline-2 outline-blue-500" : ""
                            }`}
                        aria-pressed={activeId === item.id}
                    >
                        <Image src={item.thumbSrc} alt={item.title} width={220} height={120} className="object-cover" />
                    </button>
                ))}
            </div>

            {/* Player */}
            <div className="mt-8 rounded-xl ring-1 ring-zinc-200 bg-white p-4">
                {activeItem ? (
                    <video
                        ref={(el) => {
                            videoRefs.current[activeItem.id] = el;
                        }}
                        key={activeItem.id}
                        src={activeItem.videoSrc}
                        className="w-full aspect-video rounded-md bg-black"
                        controls
                        autoPlay
                    />
                ) : null}
            </div>
        </section>
    );
}


