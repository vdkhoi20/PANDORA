import argparse

from pandora_script import PandoraConfig, PandoraRemoval


def parse_args():
    parser = argparse.ArgumentParser(description="Unified PANDORA runner for SD1.5, SD2.1, and SDXL.")
    parser.add_argument("--version", choices=["sd15", "sd21", "sdxl"], default="sd15")
    parser.add_argument("--model-path", default=None)
    parser.add_argument("--device", default=None)
    parser.add_argument("--dtype", choices=["auto", "float32", "float16", "bfloat16"], default="auto")
    parser.add_argument("--cache-dir", default=None)
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--guidance-scale", type=float, default=1.0)
    parser.add_argument("--guidance-scale-ladg", type=float, default=None)
    parser.add_argument("--percentile", type=float, default=95.0)
    parser.add_argument("--step-query", type=int, default=None)
    parser.add_argument("--layer-query", type=int, default=None)
    parser.add_argument("--image", default=None)
    parser.add_argument("--mask", default=None)
    parser.add_argument("--border-size", type=int, default=17)
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--dataset-types", nargs="*", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output", default="results/pandora")
    return parser.parse_args()


def main():
    args = parse_args()
    dtype = args.dtype
    if dtype == "auto":
        dtype = "float16" if args.version == "sdxl" else "float32"

    default_ladg = 1.3 if args.version == "sd21" else 1.6
    config = PandoraConfig(
        version=args.version,
        model_path=args.model_path,
        device=args.device,
        dtype=dtype,
        cache_dir=args.cache_dir,
        local_files_only=args.local_files_only,
        steps=args.steps,
        guidance_scale=args.guidance_scale,
        guidance_scale_ladg=args.guidance_scale_ladg if args.guidance_scale_ladg is not None else default_ladg,
        percentile=args.percentile,
        step_query=args.step_query,
        layer_query=args.layer_query,
    )
    remover = PandoraRemoval(config)

    if args.dataset:
        remover.run_dataset(args.dataset, args.output, dataset_types=args.dataset_types, limit=args.limit)
        return

    if not (args.image and args.mask):
        raise SystemExit("Single-image mode requires --image and --mask, or use --dataset.")
    remover.remove_image(args.image, args.mask, args.output, border_size=args.border_size)


if __name__ == "__main__":
    main()
