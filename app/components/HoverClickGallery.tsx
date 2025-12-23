"use client";

import { useState } from "react";

type GalleryItem = {
    id: string;
    originalSrc: string;
    resultSrc: string;
    maskSrc: string;
};

type HoverClickGalleryProps = {
    items: GalleryItem[];
    className?: string;
};

function GalleryItemComponent({ item, isClicked, isHovered, isLoading, onHover, onClick }: {
    item: GalleryItem;
    isClicked: boolean;
    isHovered: boolean;
    isLoading: boolean;
    onHover: (hover: boolean) => void;
    onClick: () => void;
}) {
    return (
        <div
            className="relative rounded-lg overflow-hidden cursor-pointer bg-gray-100 shadow-md hover:shadow-xl transition-shadow inline-block"
            onMouseEnter={() => onHover(true)}
            onMouseLeave={() => onHover(false)}
            onClick={onClick}
        >
            {/* Base image (original or result based on click state) */}
            <img
                src={isClicked ? item.resultSrc : item.originalSrc}
                alt=""
                className="block select-none"
            />

            {/* Loading overlay */}
            {isLoading && (
                <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                    <div className="text-center text-white">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
                        <div className="text-sm font-medium">Processing...</div>
                        <div className="text-xs opacity-75">Please wait ~10 seconds</div>
                    </div>
                </div>
            )}

            {/* Hover overlay - cyan only on masked (white) areas */}
            {isHovered && !isClicked && !isLoading && (
                <svg className="absolute inset-0 pointer-events-none" style={{ width: "100%", height: "100%" }}>
                    <defs>
                        <mask id={`mask-${item.id}`} maskUnits="userSpaceOnUse">
                            <image
                                href={item.maskSrc}
                                x="0"
                                y="0"
                                width="100%"
                                height="100%"
                                preserveAspectRatio="none"
                            />
                        </mask>
                    </defs>
                    <rect
                        x="0"
                        y="0"
                        width="100%"
                        height="100%"
                        fill="rgba(34, 211, 238, 0.6)"
                        mask={`url(#mask-${item.id})`}
                    />
                </svg>
            )}

            {/* Hover hint */}
            {isHovered && !isClicked && !isLoading && (
                <div className="absolute bottom-3 left-1/2 -translate-x-1/2 px-4 py-2 rounded-full bg-black/80 text-white text-sm font-medium whitespace-nowrap">
                    Click to see result
                </div>
            )}
        </div>
    );
}

export default function HoverClickGallery({ items, className }: HoverClickGalleryProps) {
    const [hoveredId, setHoveredId] = useState<string | null>(null);
    const [clickedIds, setClickedIds] = useState<Set<string>>(new Set());
    const [loadingIds, setLoadingIds] = useState<Set<string>>(new Set());

    const handleClick = (id: string) => {
        // If already clicked, toggle back to original
        if (clickedIds.has(id)) {
            setClickedIds((prev) => {
                const newSet = new Set(prev);
                newSet.delete(id);
                return newSet;
            });
        } else {
            // Show loading state
            setLoadingIds((prev) => new Set(prev).add(id));

            // Simulate processing time (10 seconds as mentioned in feedback)
            setTimeout(() => {
                setLoadingIds((prev) => {
                    const newSet = new Set(prev);
                    newSet.delete(id);
                    return newSet;
                });
                setClickedIds((prev) => new Set(prev).add(id));
            }, 10000);
        }
    };

    const handleHover = (id: string | null) => {
        setHoveredId(id);
        // Reset click state when mouse leaves (but not if loading)
        if (id === null && !loadingIds.has(hoveredId || '')) {
            setClickedIds(new Set());
        }
    };

    return (
        <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 ${className ?? ""}`}>
            {items.map((item) => (
                <GalleryItemComponent
                    key={item.id}
                    item={item}
                    isClicked={clickedIds.has(item.id)}
                    isHovered={hoveredId === item.id}
                    isLoading={loadingIds.has(item.id)}
                    onHover={(hover) => handleHover(hover ? item.id : null)}
                    onClick={() => handleClick(item.id)}
                />
            ))}
        </div>
    );
}
