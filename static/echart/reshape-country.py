# requirements:
#   pip install shapely
#
#
# notes:
#   - The script identifies country by name
#   - It then shifts longitude by -2.0 degrees, scales by 1.25× about centroid,
#     and appends a rectangle feature around the transformed country shape (with padding).
#   - Additionally, it supports asymmetric padding (more top padding) and adds a label Point
#     at the rectangle's top-left corner for use in renderers (e.g., Apache ECharts).
#   - Output is written as <input stem>_countryName.geojson next to the input.

from pathlib import Path
import json

from shapely.geometry import shape, mapping, box, Point
from shapely.affinity import translate, scale



def writeGeoJsonPretty(outputPath, data):
    try:
        # Ensure predictable key order at the top level: "type", then "features"
        topType = data.get("type", "FeatureCollection")
        features = data.get("features", [])
        if not isinstance(features, list):
            print("writeGeoJsonPretty(): 'features' must be a list")
            return

        # Build lines
        lines = []
        lines.append("{")
        lines.append(f"\"type\": \"{topType}\",")
        lines.append("\"features\": [")

        for idx1, feat in enumerate(features):
            try:
                oneLine = json.dumps(
                    feat,
                    ensure_ascii=False,
                    separators=(", ", ": ")
                )
                if idx1 < len(features) - 1:
                    lines.append(f"{oneLine},")
                else:
                    lines.append(f"{oneLine}")
            except Exception as ex:
                print(f"writeGeoJsonPretty() failed to serialize feature {idx1}: {ex}")

        lines.append("]")
        lines.append("}")

        # Join with newline to keep exactly one feature per line
        textOut = "\n".join(lines)
        Path(outputPath).write_text(textOut, encoding="utf-8")
        print(f"Wrote: {outputPath}")
    except Exception as ex:
        print(f"writeGeoJsonPretty() failed: {ex}")


def findCountryFeature( searchedCountry, feature):

    nameCandidates = []
    props = feature.get("properties", {})

    for key in props:
        # print(f"\tfindCountry({searchedCountry}) {key}")
        if key == "name":
            print(f"\tfindCountry({searchedCountry}) - found {key} -{props[key]}-")
            if props[key] == searchedCountry:
                nameCandidates.append(str(props.get(key, "")).strip())


    matchedByName = False
    for idx1, candidate in enumerate(nameCandidates):
        if searchedCountry in candidate:
            matchedByName = True

    geomDict = feature.get("geometry", None)
    if geomDict is None:
        return False
    else:
        pass
        # print(f"findCountry({searchedCountry}) geometry found")

    try:
        geom = shape(geomDict)
    except Exception as ex:
        print(f"findCountry({searchedCountry}) failed to parse geometry: {ex}")
        return False

    centroid = geom.centroid
    lonOk = centroid.x >= 30.0 and centroid.x <= 35.0
    latOk = centroid.y >= 34.0 and centroid.y <= 36.0
    matchedByHeuristic = lonOk and latOk

    # print(f"findCountry({searchedCountry}) {matchedByHeuristic=}")

    return matchedByName


def moveAndScale(geom, lonShiftDeg, latShiftDeg, scaleFactor):
    # translate by longitude shift, then scale about centroid
    moved       = translate(geom, xoff=lonShiftDeg, yoff=latShiftDeg)
    enlarged    = scale(moved, xfact=scaleFactor, yfact=scaleFactor, origin="centroid")
    return enlarged


def buildInsetRectangleAsym(geom, padLeftDeg, padRightDeg, padTopDeg, padBottomDeg):
    minx, miny, maxx, maxy = geom.bounds
    rect = box(minx - padLeftDeg, miny - padBottomDeg, maxx + padRightDeg, maxy + padTopDeg)
    return rect


def topLeftOfRectangle(rectGeom):
    minx, miny, maxx, maxy = rectGeom.bounds
    pt = Point(minx, maxy)
    return pt


def load(inputPath):
    features = []
    if not inputPath.exists():
        print(f"Input file not found: {inputPath}")
        return features

    try:
        text = inputPath.read_text(encoding="utf-8")
    except Exception as ex:
        print(f"Failed reading input: {ex}")
        return features

    try:
        data = json.loads(text)
    except Exception as ex:
        print(f"Failed parsing JSON: {ex}")
        return features

    if data.get("type") != "FeatureCollection":
        print("GeoJSON root must be a FeatureCollection.")
        return features

    features = data.get("features", [])
    if not isinstance(features, list):
        print("GeoJSON 'features' must be a list.")
        return features

    return features


def enhance(
        features, 
        countryName,
        lonShiftDeg     ,
        latShiftDeg     ,
        scaleFactor     ,
        
        padLeftDeg      ,
        padRightDeg     ,
        padTopDeg       ,
        padBottomDeg    ,

        onTopOfCountry=False,
    ):

    nameRect     =   f"{countryName} Inset Rectangle"

    namePoint    =   f"{countryName} Inset Label"
    labelPoint   =   f"{countryName} (Inset)"


    countryFound =     False
    geomTransformed   = None
    countryFeatureIdx = None

    # Identify country feature
    for idx1, feat in enumerate(features):
        try:
            if findCountryFeature(countryName , feat):
                countryFound = True
                countryFeatureIdx = idx1
                break
        except Exception as ex:
            print(f"Error during {countryName} detection at feature {idx1}: {ex}")

    if not countryFound:
        print("Did not find a feature that looks like {countryName}. No changes written.")
        return


    # Transform {countryName} geometry
    try:
        originalGeom    = shape(features[countryFeatureIdx]["geometry"])
        geomTransformed = moveAndScale(originalGeom, lonShiftDeg, latShiftDeg, scaleFactor)
        features[countryFeatureIdx]["geometry"] = mapping(geomTransformed)

        # Annotate properties so downstream users know this was modified
        if "properties" not in features[countryFeatureIdx]:
            features[countryFeatureIdx]["properties"] = {}
        features[countryFeatureIdx]["properties"]["_modified_{countryName}"] = True
        features[countryFeatureIdx]["properties"]["_lon_shift_deg"] = lonShiftDeg
        features[countryFeatureIdx]["properties"]["_scale_factor"] = scaleFactor
        print(f"transformed {countryName} geometry")
    except Exception as ex:
        print(f"Failed to transform {countryName} geometry: {ex}")
        return


    # Build and append inset rectangle (with asymmetric padding)
    try:
        insetRectGeom = buildInsetRectangleAsym(geomTransformed, padLeftDeg, padRightDeg, padTopDeg, padBottomDeg)
        insetFeature = {
            "type": "Feature",
            "properties": {
                "name": nameRect,
                "role": "inset_box",
                "padding_left_deg": padLeftDeg,
                "padding_right_deg": padRightDeg,
                "padding_top_deg": padTopDeg,
                "padding_bottom_deg": padBottomDeg
            },
            "geometry": mapping(insetRectGeom),
        }

        if onTopOfCountry:
            features.append(insetFeature)     #                     on top of 
        else:
            features.insert(0, insetFeature)  # prepend - rectangle under country
        print(f"rectangle around {countryName} with asymmetric padding")
    
    except Exception as ex:
        print(f"Failed to create inset rectangle: {ex}")
        return



    if False:
        # Add a label point at the rectangle's top-left corner
        try:
            tlPoint = topLeftOfRectangle(insetRectGeom)
            labelFeature = {
                "type": "Feature",
                "properties": {
                    "name":     namePoint,
                    "role":     "inset_label",
                    "label":    labelPoint,
                    "anchor":   "top-left",
                    # pixels; to be interpreted by the renderer (e.g., ECharts)
                    "offset_px": [-10, -8],   #  first -10 -  move to the left - why is not already left ---       second  -8 to move vertically up
                },
                "geometry": mapping(tlPoint),
            }
            features.append(labelFeature)
            print("added inset label point at top-left")
        except Exception as ex:
            print(f"Failed to add label point: {ex}")
            return


def roundCoords(features, decimals=3):
    """
    Rounds all coordinate values in all features' geometries
    to the specified number of decimal places.
    """

    def roundCoordList(coordList):
        if isinstance(coordList[0], (float, int)):
            # Single coordinate pair
            return [round(coordList[0], decimals), round(coordList[1], decimals)]
        else:
            # Nested list of coordinates
            newList = []
            for idx1, sub in enumerate(coordList):
                newList.append(roundCoordList(sub))
            return newList

    for idx1, feat in enumerate(features):
        try:
            geom = feat.get("geometry", None)
            if geom is None:
                continue

            coords = geom.get("coordinates", None)
            if coords is None:
                continue

            geom["coordinates"] = roundCoordList(coords)
            feat["geometry"] = geom
        except Exception as ex:
            print(f"roundCoords() failed on feature {idx1}: {ex}")



def dropClosePoints(features, minDistance=0.005):
    """
    Removes redundant coordinate points from geometries:
    if a point is not farther than 'minDistance' from the
    previous kept point (in degrees), it is dropped.

    Works recursively for all geometry coordinate structures.
    """

    import math

    def distance(p1, p2):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return math.sqrt(dx * dx + dy * dy)

    def filterCoords(coordList):
        # Single coordinate pair?
        if isinstance(coordList[0], (float, int)):
            return coordList

        # Nested: list of coordinates
        newList = []

        # Determine if this is a list of coordinate pairs or deeper nesting
        if isinstance(coordList[0][0], (float, int)):
            # List of coordinate pairs → apply distance filter
            if len(coordList) == 0:
                return coordList

            # Always keep first point
            newList.append(coordList[0])

            for idx1 in range(1, len(coordList)):
                prev = newList[-1]
                curr = coordList[idx1]
                dist = distance(prev, curr)
                if dist > minDistance:
                    newList.append(curr)
                else:
                    print(f"\tdropped close point {curr[0]:6.3f}:{curr[1]:6.3f} -  dist={dist:.4f}")

            return newList

        else:
            # Deeper nesting (Polygon rings, MultiPolygons, etc.)
            nested = []
            for idx1, sub in enumerate(coordList):
                nested.append(filterCoords(sub))
            return nested

    # ---- feature iteration ----
    for idx1, feat in enumerate(features):
        try:
            geom = feat.get("geometry", None)
            if geom is None:
                print(f"dropClosePoints(): feature {idx1} has no geometry")
                continue

            coords = geom.get("coordinates", None)
            if coords is None:
                print(f"dropClosePoints(): feature {idx1} has no coordinates")
                continue

            geom["coordinates"] = filterCoords(coords)
            feat["geometry"] = geom

        except Exception as ex:
            print(f"dropClosePoints() failed on feature {idx1}: {ex}")


def main():

    inputPath       = Path("./europe-reduced-orig.geojson")
    features = load(inputPath)
    if len(features) < 1:
        return


    countryName = "Cyprus"


    # ----- configuration -----
    lonShiftDeg     =   1.8
    latShiftDeg     =   0.5
    scaleFactor     =   1.25

    padLeftDeg      =   0.60
    padRightDeg     =   0.60
    padTopDeg       =   0.65    # <- increase top padding here
    padBottomDeg    =   0.60

    # -------------------------

    enhance(
        features, 
        countryName,
            
        lonShiftDeg     ,
        latShiftDeg     ,
        scaleFactor     ,

        padLeftDeg      ,
        padRightDeg     ,
        padTopDeg       ,
        padBottomDeg    ,

    )

    enhance(
        features, 
        "Malta",
            
        lonShiftDeg    =  -2.5 ,
        latShiftDeg    =  -0.7  ,
        scaleFactor    =   3.5  ,

        padLeftDeg     = 0.9 ,
        padRightDeg    = 0.9 ,
        padTopDeg      = 0.4 ,
        padBottomDeg   = 0.6 ,

    )


    enhance(
        features, 
        "Luxembourg",
            
        lonShiftDeg    =   0.0 ,
        latShiftDeg    =  -0.0  ,
        scaleFactor    =   1.3  ,

        padLeftDeg     = 0.4 ,
        padRightDeg    = 0.4 ,
        padTopDeg      = 0.4 ,
        padBottomDeg   = 0.4 ,

        # onTopOfCountry=True,

    )


    # Round all coordinates to 3 decimals
    try:
        roundCoords(features, decimals=3)
        print("Rounded all coordinates to 3 decimals")
    except Exception as ex:
        print(f"Failed rounding coordinates: {ex}")


    # Then drop redundant points
    # dropClosePoints(features, minDistance=0.005)
    dropClosePoints(features, minDistance=0.080)

    # Write output (top-level lines + one-line features)
    try:
        outputPath = inputPath.with_name(f"{inputPath.stem}_{countryName.lower()}.geojson")
        outputPath = Path("europe-reduced.geojson")  # keep your override
        dataOut = {
            "type": "FeatureCollection",
            "features": features
        }
        writeGeoJsonPretty(outputPath, dataOut)
    except Exception as ex:
        print(f"Failed writing output: {ex}")
        return

if __name__ == "__main__":
    main()
