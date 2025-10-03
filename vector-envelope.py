from pathlib import Path
import sys
import math

import numpy as np
from   PIL import Image
import cv2  # pip install opencv-python



from pathlib import Path

def normalizeForTokens(pathD: str) -> list[str]:
    cmdSet = set("MmLlHhVvZz")
    outChars = []
    i = 0
    while i < len(pathD):
        ch = pathD[i]
        if ch in cmdSet:
            outChars.append(" ")
            outChars.append(ch.upper())
            outChars.append(" ")
            i = i + 1
        elif ch == ",":
            outChars.append(" ")
            i = i + 1
        elif ch == "-":
            if i > 0:
                prev = pathD[i - 1]
                if prev not in " ,\t\r\nEe-+":
                    outChars.append(" ")
            outChars.append("-")
            i = i + 1
        else:
            outChars.append(ch)
            i = i + 1
    return "".join(outChars).split()

def formatNumber(n: float) -> str:
    i = int(round(n))
    if abs(n - i) < 1e-9:
        return str(i)
    s = f"{n:.6f}"
    s = s.rstrip("0").rstrip(".")
    return s

def offsetPathDValid(pathD: str, dx: float, dy: float) -> str:
    tokens = normalizeForTokens(pathD)
    out = []
    i = 0
    currentCmd = None
    movePairEmitted = False
    try:
        while i < len(tokens):
            t = tokens[i]
            if t in ("M", "L", "H", "V", "Z"):
                currentCmd = t
                i = i + 1
                if currentCmd == "Z":
                    if len(out) > 0 and out[-1] != "Z":
                        out.append("Z")
                    continue
                if currentCmd == "H":
                    if i >= len(tokens):
                        raise ValueError("Expected x after H")
                    x = float(tokens[i]); i = i + 1
                    x = x + dx
                    out.append("H"); out.append(formatNumber(x))
                    continue
                if currentCmd == "V":
                    if i >= len(tokens):
                        raise ValueError("Expected y after V")
                    y = float(tokens[i]); i = i + 1
                    y = y + dy
                    out.append("V"); out.append(formatNumber(y))
                    continue
                if currentCmd == "M":
                    movePairEmitted = False
                continue

            if currentCmd is None:
                currentCmd = "L"

            if currentCmd in ("M", "L"):
                # consume coordinate pairs
                while i + 1 < len(tokens):
                    if tokens[i] in ("M", "L", "H", "V", "Z"):
                        break
                    x = float(tokens[i]);   i = i + 1
                    y = float(tokens[i]);   i = i + 1
                    x = x + dx
                    y = y + dy
                    if currentCmd == "M" and not movePairEmitted:
                        out.append("M"); out.append(formatNumber(x)); out.append(formatNumber(y))
                        movePairEmitted = True
                        currentCmd = "L"
                    else:
                        out.append("L"); out.append(formatNumber(x)); out.append(formatNumber(y))
                currentCmd = None
                continue

            raise ValueError(f"Unsupported token: {t}")
        # build a valid 'd' with spaces between tokens
        dParts = []
        j = 0
        while j < len(out):
            dParts.append(out[j])
            j = j + 1
        return " ".join(dParts)
    except Exception as ex:
        print(f"Error: {ex}")
        raise




def loadImageAsMask(imagePath: Path, alphaThreshold: int = 8, fallbackGrayThreshold: int = 230) -> np.ndarray:
    img = Image.open(imagePath).convert("RGBA")
    w, h = img.size
    rgba = np.array(img)
    alpha = rgba[:, :, 3]

    if np.any(alpha < 255):
        mask = (alpha > alphaThreshold).astype(np.uint8) * 255
    else:
        gray = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
        mask = (gray < fallbackGrayThreshold).astype(np.uint8) * 255

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    return mask

def inflateMask(mask: np.ndarray, marginPx: int) -> np.ndarray:
    if marginPx <= 0:
        return mask
    diameter = max(1, marginPx * 2 + 1)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (diameter, diameter))
    dilated = cv2.dilate(mask, kernel, iterations=1)
    return dilated

def getLargestContour(mask: np.ndarray) -> np.ndarray:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if len(contours) == 0:
        raise RuntimeError("No contour found. Is the image transparent everywhere?")
    largest = contours[0]
    maxArea = cv2.contourArea(largest)
    for i in range(len(contours)):
        c = contours[i]
        area = cv2.contourArea(c)
        if area > maxArea:
            largest = c
            maxArea = area
    return largest

def simplifyContour(contour: np.ndarray, epsilonRatio: float = 0.015) -> np.ndarray:
    perimeter = cv2.arcLength(contour, True)
    epsilon = max(1.0, epsilonRatio * perimeter)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    return approx

def getTightBoundingBox(contour: np.ndarray) -> tuple[int, int, int, int]:
    # returns (minX, minY, width, height)
    x, y, w, h = cv2.boundingRect(contour)
    return int(x), int(y), int(w), int(h)

def translateContour(contour: np.ndarray, dx: int, dy: int) -> np.ndarray:
    shifted = contour.copy()
    for i in range(shifted.shape[0]):
        shifted[i, 0, 0] = int(shifted[i, 0, 0] + dx)
        shifted[i, 0, 1] = int(shifted[i, 0, 1] + dy)
    return shifted

def contourToSvgPath(contour: np.ndarray) -> str:
    points = []
    for i in range(contour.shape[0]):
        x = int(contour[i, 0, 0])
        y = int(contour[i, 0, 1])
        points.append((x, y))

    if len(points) == 0:
        raise RuntimeError("Empty contour after simplification.")

    parts = []
    first = points[0]
    parts.append(f"M{first[0]} {first[1]}")
    for i in range(1, len(points)):
        px = points[i][0]
        py = points[i][1]
        parts.append(f"L{px} {py}")
    parts.append("Z")

    d = " ".join(parts)
    return d

def writeSvgWithPath(pathD: str, viewW: int, viewH: int, outPath: Path, debugStroke: bool = True) -> None:
    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {viewW} {viewH}" width="{viewW}" height="{viewH}">')
    lines.append(f'  <path d="{pathD}" fill="black" />')
    if debugStroke:
        lines.append(f'  <path d="{pathD}" fill="none" stroke="magenta" stroke-width="2" vector-effect="non-scaling-stroke"/>')
        lines.append(f'  <rect x="0" y="0" width="{viewW}" height="{viewH}" fill="none" stroke="orange" stroke-dasharray="6 6" opacity="0.5" vector-effect="non-scaling-stroke"/>')
    lines.append('</svg>')

    text = "\n".join(lines)
    outPath.write_text(text, encoding="utf-8")

def main():
    # --- configure ---
    inpPth = Path("./img/symbols/interest-rates-hourglass-blue.png")
    svgFullPth  = inpPth.with_name(inpPth.stem + "_full.svg")
    svgTightPth = inpPth.with_name(inpPth.stem + "_tight.svg")

    marginPx     = 4          # grow outline (like shape-margin)
    epsilonRatio = 0.015      # larger → rougher / fewer points

    # If you paste inside a larger container (e.g., 700x420) and want the path centered horizontally,
    # set these to get a ready-to-paste <g transform="translate(... ...)> snippet.
    containerW = 700
    containerH = 420
    topY       = 60           # vertical placement of the image top inside the container

    try:
        mask    = loadImageAsMask(inpPth)
        mask    = inflateMask(mask, marginPx)
        contour = getLargestContour(mask)
        contour = simplifyContour(contour, epsilonRatio=epsilonRatio)

        # Image size
        with Image.open(inpPth) as im:
            imgW, imgH = im.size



        # Full-canvas path (coordinates in image space)
        pathFull = contourToSvgPath(contour)

        # Tight box + normalized path
        minX, minY, boxW, boxH = getTightBoundingBox(contour)
        contourNorm = translateContour(contour, dx=-minX, dy=-minY)
        pathTight = contourToSvgPath(contourNorm)

        # Write two helper SVGs
        writeSvgWithPath(pathFull,  imgW, imgH, svgFullPth,  debugStroke=True)
        writeSvgWithPath(pathTight, boxW, boxH, svgTightPth, debugStroke=True)

        # Console output for copy/paste
        print("imageViewBox:",      f"0 0 {imgW} {imgH}")
        print("tightViewBox:",      f"0 0 {boxW} {boxH}")
        print("offsetWithinImage:", f"{minX} {minY}")
        print()
        print("pathD_full_imageCoords:")
        print(pathFull)
        print()
        print("pathD_tight_normalized:")
        print(pathTight)
        print()

        # Placement snippet for a larger container (centered horizontally)
        pasteX = int(containerW / 2 - imgW / 2)
        pasteY = int(topY)
        print("pasteIntoContainer_example (centered horizontally):")
        print(f'<g transform="translate({pasteX} {pasteY})"><path d="{pathFull}" fill="#000"/></g>')

        print(pathFull)
        print(offsetPathDValid(pathFull, 234, 60))


    except Exception as ex:
        print(f"Error: {ex}")
        sys.exit(1)

if __name__ == "__main__":
    main()
