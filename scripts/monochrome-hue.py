#!/usr/bin/env python3

"""
Monochrome hue filter for RGB JPEGs.

    python monochrome-hue.py  ./inp.jpg                    --brighten=1.4
    python monochrome-hue.py  ./inp.jpg  --saturation=0.6  --brighten=1.6
    python monochrome-hue.py  ./inp.jpg  --saturation=0.8  --brighten=1.8
    python monochrome-hue.py  ./inp.jpg  --saturation=0.4  --brighten=1.8


"""


from pathlib import Path
from typing import Tuple
import argparse
from PIL import Image, ImageOps
from colorsys import rgb_to_hsv, hsv_to_rgb





def clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x

def applyMonochrome(inputPath: Path, outputPath: Path, targetRgb: Tuple[int, int, int],
    quality: int,
    saturation: float,
    brightenFactor: float,
) -> None:
    try:
        with Image.open(inputPath) as srcImg:
            if srcImg.mode not in ("RGB", "RGBA"):
                srcImg = srcImg.convert("RGB")

            width, height = srcImg.size
            grayImg = srcImg.convert("L")

            # target → HSV
            tR = targetRgb[0] / 255.0
            tG = targetRgb[1] / 255.0
            tB = targetRgb[2] / 255.0
            hT, sT, vT = rgb_to_hsv(tR, tG, tB)

            sMul = clamp01(float(saturation))
            bMul = float(brightenFactor)

            outImg = Image.new("RGB", (width, height))
            grayPx = grayImg.load()
            outPx = outImg.load()

            y = 0
            while y < height:
                x = 0
                while x < width:
                    g = grayPx[x, y] / 255.0        # grayscale 0..1
                    s = clamp01(sT * sMul)          # keep target’s saturation, scaled
                    v = clamp01(g * vT * bMul)      # keep target’s value, scaled
                    rF, gF, bF = hsv_to_rgb(hT, s, v)
                    r = int(round(rF * 255))
                    g2 = int(round(gF * 255))
                    b = int(round(bF * 255))
                    outPx[x, y] = (r, g2, b)
                    x += 1
                y += 1

            outputPath.parent.mkdir(parents=True, exist_ok=True)
            outImg.save(outputPath, format="JPEG", quality=int(quality), subsampling="4:4:4", optimize=True)

            print(f"Saved: {outputPath}")
            print(f"H={hT:.4f}  sT={sT:.4f}  vT={vT:.4f}  saturationMul={sMul:.3f}  brightenMul={bMul:.3f}")
            print("Note: saturation=1.0 and brighten=1.0 reproduces target RGB at white.")
    except Exception as exc:
        print(f"Error in applyMonochrome: {exc}")
        raise


def applyLinearRgbTint(inputPath: Path, outputPath: Path, targetRgb: Tuple[int, int, int], quality: int) -> None:
    try:
        with Image.open(inputPath) as srcImg:
            if srcImg.mode not in ("RGB", "RGBA"):
                srcImg = srcImg.convert("RGB")

            grayImg = srcImg.convert("L")
            width, height = grayImg.size
            grayPx = grayImg.load()

            outImg = Image.new("RGB", (width, height))
            outPx = outImg.load()

            tR = targetRgb[0]
            tG = targetRgb[1]
            tB = targetRgb[2]

            y = 0
            while y < height:
                x = 0
                while x < width:
                    g = grayPx[x, y] / 255.0
                    r = int(round(g * tR))
                    g2 = int(round(g * tG))
                    b = int(round(g * tB))
                    outPx[x, y] = (r, g2, b)
                    x += 1
                y += 1

            outputPath.parent.mkdir(parents=True, exist_ok=True)
            outImg.save(outputPath, format="JPEG", quality=quality, subsampling="4:4:4", optimize=True)

            print(f"Tint applied linearly in RGB space. Target color: {targetRgb}")
            print(f"Saved to {outputPath}")

    except Exception as exc:
        print(f"Error in applyLinearRgbTint: {exc}")
        raise




def parseArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tint an image to a single hue.")
    parser.add_argument("inputPath", type=Path)
    parser.add_argument("--rgb",        type=int,   nargs=3,  metavar=("R","G","B"), default=(174, 215, 217))
    parser.add_argument("--quality",    type=int,   default=95)
    parser.add_argument("--saturation", type=float, default=1.0, help="0..1; higher = stronger tint")
    parser.add_argument("--brighten",   type=float, default=1.0, help="Optionally brighten - i.e. 20% (multiplies Value by 1.2)")
    return parser.parse_args()


def main() -> None:
    args = parseArgs()
    inp = Path(args.inputPath)
    rgb = (int(args.rgb[0]), int(args.rgb[1]), int(args.rgb[2]))

    # rgb = (174, 215, 217)
    rgb = (194, 211,  0)

    saturation      = float(args.saturation)
    brightenFactor  = float(args.brighten)

    out = inp.with_name(inp.stem + f"--{rgb[0]}-{rgb[1]}-{rgb[2]}.jpg")
    applyLinearRgbTint(
        inp, 
        out, 
        rgb, 
        int(args.quality),
        # saturation,
        # brightenFactor,        
    )

    out = inp.with_name(inp.stem + f"--sat{saturation:3.1f}--{brightenFactor:3.1f}--{rgb[0]}-{rgb[1]}-{rgb[2]}.jpg")
    applyMonochrome(
        inp, 
        out, 
        rgb, 
        int(args.quality),
        saturation,
        brightenFactor,        
    )


if __name__ == "__main__":
    main()
