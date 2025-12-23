"use client";

import { useCallback, useEffect, useRef, useState } from "react";

type BeforeAfterSliderProps = {
    beforeSrc: string;
    afterSrc: string;
    alt?: string;
    label?: string;
    className?: string;
};

export default function BeforeAfterSlider({
    beforeSrc,
    afterSrc,
    alt = "",
    label,
    className,
}: BeforeAfterSliderProps) {
    const containerRef = useRef<HTMLDivElement | null>(null);
    const [positionPx, setPositionPx] = useState<number | null>(null);
    const [containerWidth, setContainerWidth] = useState(0);

    const clamp = (value: number, min: number, max: number) =>
        Math.max(min, Math.min(max, value));

    const updateFromClientX = useCallback(
        (clientX: number) => {
            if (!containerRef.current) return;
            const rect = containerRef.current.getBoundingClientRect();
            const x = clamp(clientX - rect.left, 0, rect.width);
            setPositionPx(x);
        },
        [containerRef]
    );

    useEffect(() => {
        if (!containerRef.current) return;
        setContainerWidth(containerRef.current.clientWidth);
        const observer = new ResizeObserver((entries) => {
            for (const entry of entries) {
                setContainerWidth(entry.contentRect.width);
            }
        });
        observer.observe(containerRef.current);
        return () => observer.disconnect();
    }, []);

    // Initialize handle in the center
    useEffect(() => {
        if (positionPx === null && containerWidth > 0) {
            setPositionPx(containerWidth / 2);
        }
    }, [containerWidth, positionPx]);

    const onPointerDown = (e: React.PointerEvent) => {
        (e.target as Element).setPointerCapture(e.pointerId);
        updateFromClientX(e.clientX);
    };

    const onPointerMove = (e: React.PointerEvent) => {
        if (e.pressure === 0) return; // not dragging
        updateFromClientX(e.clientX);
    };

    const onKeyDown = (e: React.KeyboardEvent) => {
        if (positionPx === null || !containerRef.current) return;
        const delta = Math.max(4, Math.round(containerRef.current.clientWidth * 0.02));
        if (e.key === "ArrowLeft") setPositionPx(clamp(positionPx - delta, 0, containerRef.current.clientWidth));
        if (e.key === "ArrowRight") setPositionPx(clamp(positionPx + delta, 0, containerRef.current.clientWidth));
    };

    const handleLeft = positionPx ?? 0;
    const clipWidth = positionPx ?? containerWidth / 2;

    return (
        <figure
            className={`relative overflow-hidden rounded bg-zinc-100 dark:bg-zinc-900 inline-block ${className ?? ""}`}
            ref={containerRef}
        >
            {/* After image (full) */}
            <img src={afterSrc} alt={alt} className="block select-none" />

            {/* Before image (clipped) */}
            <div className="absolute inset-0 overflow-hidden" style={{ width: clipWidth }}>
                <div className="relative" style={{ width: containerWidth }}>
                    <img src={beforeSrc} alt={alt} className="w-full h-auto select-none block" />
                </div>
            </div>

            {/* Divider line */}
            <div
                className="absolute top-0 bottom-0 w-px bg-white/80 dark:bg-white/60 shadow-[0_0_0_1px_rgba(0,0,0,0.2)]"
                style={{ left: handleLeft - 0.5 }}
                aria-hidden="true"
            />

            {/* Handle */}
            <div
                role="slider"
                aria-label={label ?? "Before/after slider"}
                aria-valuemin={0}
                aria-valuemax={containerWidth}
                aria-valuenow={positionPx ?? containerWidth / 2}
                tabIndex={0}
                className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 h-10 w-10 rounded-full bg-white/90 text-zinc-800 dark:text-zinc-900 shadow flex items-center justify-center cursor-ew-resize outline-none ring-0 focus:ring-2 focus:ring-blue-500"
                style={{ left: handleLeft }}
                onPointerDown={onPointerDown}
                onPointerMove={onPointerMove}
                onKeyDown={onKeyDown}
            >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <polyline points="15 18 9 12 15 6" />
                </svg>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <polyline points="9 18 15 12 9 6" />
                </svg>
            </div>

            {label ? (
                <figcaption className="absolute bottom-3 right-3 text-sm px-3 py-1 rounded bg-black/60 text-white">
                    {label}
                </figcaption>
            ) : null}
        </figure>
    );
}


