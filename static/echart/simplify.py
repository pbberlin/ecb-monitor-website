#!/usr/bin/env python3

from pathlib import Path
import json
import math
import hashlib
from typing import List, Tuple, Dict, Any

def roundCoord(coord, decimals):
    x = round(float(coord[0]), decimals)
    y = round(float(coord[1]), decimals)
    return (x, y)

def edgeKey(p1, p2, decimals):
    a = roundCoord(p1, decimals)
    b = roundCoord(p2, decimals)
    if a <= b:
        return (a, b)
    else:
        return (b, a)

def ringIsClosed(coords):
    if len(coords) == 0:
        return False
    first = coords[0]
    last = coords[-1]
    return (first[0] == last[0]) and (first[1] == last[1])

def closeRingIfNeeded(coords):
    if ringIsClosed(coords) is False:
        newCoords = []
        index = 0
        while index < len(coords):
            p = coords[index]
            newCoords.append((float(p[0]), float(p[1])))
            index += 1
        first = newCoords[0]
        newCoords.append((first[0], first[1]))
        return newCoords
    else:
        newCoords = []
        index = 0
        while index < len(coords):
            p = coords[index]
            newCoords.append((float(p[0]), float(p[1])))
            index += 1
        return newCoords

def openRing(coords):
    newCoords = []
    lastIndex = len(coords) - 1
    index = 0
    while index < lastIndex:
        newCoords.append(coords[index])
        index += 1
    return newCoords

def hashForAnchor(roundedCoords):
    m = hashlib.sha256()
    index = 0
    while index < len(roundedCoords):
        pair = roundedCoords[index]
        m.update(str(pair[0]).encode("utf-8"))
        m.update(str(pair[1]).encode("utf-8"))
        index += 1
    digest = m.hexdigest()
    value = int(digest[:8], 16)
    return value

def averageGroup(points):
    sumX = 0.0
    sumY = 0.0
    count = 0
    index = 0
    while index < len(points):
        sumX += float(points[index][0])
        sumY += float(points[index][1])
        count += 1
        index += 1
    if count == 0:
        return None
    avgX = sumX / float(count)
    avgY = sumY / float(count)
    return (avgX, avgY)

def dist(p, q):
    dx = float(q[0]) - float(p[0])
    dy = float(q[1]) - float(p[1])
    return math.hypot(dx, dy)

def simplifySequenceByDistance(seq, thresholdDistance):
    # Cluster consecutive points: if distance to previous point <= thresholdDistance,
    # keep extending the cluster; otherwise, finalize previous cluster by averaging.
    simplified = []
    if len(seq) == 0:
        return simplified

    currentCluster = []
    index = 0
    while index < len(seq):
        p = seq[index]
        if len(currentCluster) == 0:
            currentCluster.append(p)
        else:
            prev = currentCluster[-1]
            d = dist(prev, p)
            if d <= thresholdDistance:
                currentCluster.append(p)
            else:
                avg = averageGroup(currentCluster)
                if avg is not None:
                    simplified.append(avg)
                currentCluster = []
                currentCluster.append(p)
        index += 1

    if len(currentCluster) > 0:
        avg = averageGroup(currentCluster)
        if avg is not None:
            simplified.append(avg)

    return simplified

def canonicalizeChunkDirection(chunkRounded):
    if len(chunkRounded) == 0:
        return ([], False)
    start = chunkRounded[0]
    end = chunkRounded[-1]
    if start <= end:
        return (chunkRounded, False)
    else:
        reversedChunk = []
        index = len(chunkRounded) - 1
        while index >= 0:
            reversedChunk.append(chunkRounded[index])
            index -= 1
        return (reversedChunk, True)

def splitRingIntoChunks(coordsOpen, sharedEdgeSet, decimals):
    chunks = []
    if len(coordsOpen) == 0:
        return chunks

    current = {
        "coords": [],
        "shared": None
    }

    index = 0
    while index < len(coordsOpen):
        p = coordsOpen[index]
        nextIndex = (index + 1) % len(coordsOpen)
        q = coordsOpen[nextIndex]
        k = edgeKey(p, q, decimals)
        isShared = k in sharedEdgeSet

        if current["shared"] is None:
            current["shared"] = isShared
            current["coords"].append(p)
        else:
            if isShared == current["shared"]:
                current["coords"].append(p)
            else:
                chunks.append({
                    "coords": current["coords"][:],
                    "shared": current["shared"]
                })
                current = {
                    "coords": [p],
                    "shared": isShared
                }

        index += 1

    if len(coordsOpen) > 0:
        current["coords"].append(coordsOpen[0])

    chunks.append({
        "coords": current["coords"][:],
        "shared": current["shared"]
    })

    normalized = []
    i = 0
    while i < len(chunks):
        ch = chunks[i]
        points = ch["coords"]
        openPoints = []
        j = 0
        while j < (len(points) - 1):
            openPoints.append(points[j])
            j += 1
        normalized.append({
            "coords": openPoints,
            "shared": ch["shared"]
        })
        i += 1

    return normalized

def rebuildClosedRingFromChunks(simplifiedChunks):
    rebuilt = []
    i = 0
    while i < len(simplifiedChunks):
        part = simplifiedChunks[i]
        j = 0
        while j < len(part):
            rebuilt.append(part[j])
            j += 1
        i += 1
    if len(rebuilt) == 0:
        return []
    first = rebuilt[0]
    rebuilt.append((first[0], first[1]))
    return rebuilt

def computeDatasetExtent(features):
    minX = float("inf")
    minY = float("inf")
    maxX = float("-inf")
    maxY = float("-inf")

    fi = 0
    while fi < len(features):
        feat = features[fi]
        geom = feat.get("geometry", {})
        coords = geom.get("coordinates", None)
        gtype = geom.get("type", None)

        if gtype == "Polygon":
            ri = 0
            while coords is not None and ri < len(coords):
                ring = coords[ri]
                pj = 0
                while pj < len(ring):
                    p = ring[pj]
                    x = float(p[0])
                    y = float(p[1])
                    if x < minX:
                        minX = x
                    if x > maxX:
                        maxX = x
                    if y < minY:
                        minY = y
                    if y > maxY:
                        maxY = y
                    pj += 1
                ri += 1

        elif gtype == "MultiPolygon":
            pi = 0
            while coords is not None and pi < len(coords):
                rings = coords[pi]
                ri = 0
                while ri < len(rings):
                    ring = rings[ri]
                    pj = 0
                    while pj < len(ring):
                        p = ring[pj]
                        x = float(p[0])
                        y = float(p[1])
                        if x < minX:
                            minX = x
                        if x > maxX:
                            maxX = x
                        if y < minY:
                            minY = y
                        if y > maxY:
                            maxY = y
                        pj += 1
                    ri += 1
                pi += 1
        else:
            # ignore non-polygons for extent
            pass

        fi += 1

    if minX == float("inf"):
        return (0.0, 0.0, 0.0, 0.0)

    return (minX, minY, maxX, maxY)

def simplifyGeoJsonTopologically(inputPath, outputPath, simplifyPercent, matchPrecision):
    try:
        data = None
        with inputPath.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read GeoJSON: {e}")
        return

    features = []
    if "type" in data and data["type"] == "FeatureCollection":
        features = data.get("features", [])
    elif "type" in data and data["type"] == "Feature":
        features = [data]
    else:
        print("Unsupported GeoJSON root. Expected FeatureCollection or Feature.")
        return

    # Compute proximity threshold from dataset extent
    minX, minY, maxX, maxY = computeDatasetExtent(features)
    spanX = maxX - minX
    spanY = maxY - minY
    span = max(spanX, spanY)
    factor = float(simplifyPercent) / 100.0
    thresholdDistance = span * factor

    # Index edges to identify shared borders
    edgeCount: Dict[Tuple[Tuple[float, float], Tuple[float, float]], int] = {}
    allFeatureRings: List[Dict[str, Any]] = []

    fi = 0
    while fi < len(features):
        feat = features[fi]
        geom = feat.get("geometry", {})
        gtype = geom.get("type", None)
        coords = geom.get("coordinates", None)

        if gtype == "Polygon":
            rings = coords if coords is not None else []
            ri = 0
            while ri < len(rings):
                ring = closeRingIfNeeded(rings[ri])
                allFeatureRings.append({
                    "featureIndex": fi,
                    "ringIndex": ri,
                    "coordsClosed": ring
                })
                j = 0
                while j < (len(ring) - 1):
                    k = edgeKey(ring[j], ring[j+1], matchPrecision)
                    edgeCount[k] = edgeCount.get(k, 0) + 1
                    j += 1
                ri += 1

        elif gtype == "MultiPolygon":
            mp = coords if coords is not None else []
            pi = 0
            while pi < len(mp):
                rings = mp[pi]
                ri = 0
                while ri < len(rings):
                    ring = closeRingIfNeeded(rings[ri])
                    allFeatureRings.append({
                        "featureIndex": fi,
                        "multiPolygonIndex": pi,
                        "ringIndex": ri,
                        "coordsClosed": ring
                    })
                    j = 0
                    while j < (len(ring) - 1):
                        k = edgeKey(ring[j], ring[j+1], matchPrecision)
                        edgeCount[k] = edgeCount.get(k, 0) + 1
                        j += 1
                    ri += 1
                pi += 1
        else:
            pass

        fi += 1

    sharedEdgeSet = set()
    for k, c in edgeCount.items():
        if c > 1:
            sharedEdgeSet.add(k)

    # Cache for simplified shared chunks to guarantee identical results on both sides
    sharedChunkCache: Dict[str, List[Tuple[float, float]]] = {}

    ringOutputs: Dict[Tuple[int, int, int], List[Tuple[float, float]]] = {}

    r = 0
    while r < len(allFeatureRings):
        item = allFeatureRings[r]
        coordsClosed = item["coordsClosed"]
        coordsOpen = openRing(coordsClosed)

        chunks = splitRingIntoChunks(coordsOpen, sharedEdgeSet, matchPrecision)
        simplifiedChunks: List[List[Tuple[float, float]]] = []

        ci = 0
        while ci < len(chunks):
            ch = chunks[ci]
            chCoords = ch["coords"]

            rounded = []
            idx = 0
            while idx < len(chCoords):
                rounded.append(roundCoord(chCoords[idx], matchPrecision))
                idx += 1

            canonicalRounded, reversedFromOriginal = canonicalizeChunkDirection(rounded)

            canonicalKeyParts = []
            j = 0
            while j < len(canonicalRounded):
                canonicalKeyParts.append(f"{canonicalRounded[j][0]},{canonicalRounded[j][1]}")
                j += 1
            canonicalKey = "|".join(canonicalKeyParts)

            # Simplify: use cache for shared chunks so borders are identical
            if ch["shared"] is True:
                if canonicalKey in sharedChunkCache:
                    simpCanon = sharedChunkCache[canonicalKey]
                else:
                    simpCanon = simplifySequenceByDistance(canonicalRounded, thresholdDistance)
                    sharedChunkCache[canonicalKey] = simpCanon
            else:
                simpCanon = simplifySequenceByDistance(canonicalRounded, thresholdDistance)

            if reversedFromOriginal is True:
                simpChunk = []
                k = len(simpCanon) - 1
                while k >= 0:
                    simpChunk.append(simpCanon[k])
                    k -= 1
            else:
                simpChunk = []
                m = 0
                while m < len(simpCanon):
                    simpChunk.append(simpCanon[m])
                    m += 1

            simplifiedChunks.append(simpChunk)
            ci += 1

        rebuiltClosed = rebuildClosedRingFromChunks(simplifiedChunks)

        if len(rebuiltClosed) < 4:
            rebuiltClosed = coordsClosed[:]

        featureIndex = item["featureIndex"]
        multiPolygonIndex = item.get("multiPolygonIndex", -1)
        ringIndex = item["ringIndex"]
        ringOutputs[(featureIndex, multiPolygonIndex, ringIndex)] = rebuiltClosed
        r += 1

    fi = 0
    while fi < len(features):
        feat = features[fi]
        geom = feat.get("geometry", {})
        gtype = geom.get("type", None)
        if gtype == "Polygon":
            rings = geom.get("coordinates", [])
            newRings = []
            ri = 0
            while ri < len(rings):
                key = (fi, -1, ri)
                ring = ringOutputs.get(key, closeRingIfNeeded(rings[ri]))
                newRings.append(ring)
                ri += 1
            geom["coordinates"] = newRings

        elif gtype == "MultiPolygon":
            mp = geom.get("coordinates", [])
            newMP = []
            pi = 0
            while pi < len(mp):
                rings = mp[pi]
                newRings = []
                ri = 0
                while ri < len(rings):
                    key = (fi, pi, ri)
                    ring = ringOutputs.get(key, closeRingIfNeeded(rings[ri]))
                    newRings.append(ring)
                    ri += 1
                newMP.append(newRings)
                pi += 1
            geom["coordinates"] = newMP
        else:
            pass

        fi += 1

    try:
        with Path(outputPath).open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to write output: {e}")

def main():
    inputPath  = Path("europe-reduced.geojson")  
    outputPath = Path("europe-reduced-simplified.geojson")

    # Example: 0.1 percent of dataset span → threshold
    simplifyPercent = 0.1

    # Controls detection of shared borders and canonicalization precision
    matchPrecision = 7

    # If you want to use the attached file in this session, uncomment:
    # inputPath = Path("/mnt/data/acd7e0a5-1fa5-43eb-ab7a-c02e2c291aee.geojson")

    simplifyGeoJsonTopologically(inputPath, outputPath, simplifyPercent, matchPrecision)
    print(f"Done. Wrote: {outputPath}")

if __name__ == "__main__":
    main()
