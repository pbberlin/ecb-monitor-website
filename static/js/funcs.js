/*
    ecb-monitor.zew.de

    global funcs
*/


// color funcs start
function mapToZeroOne(vl, ranges) {

    let range0 = ranges[0];
    let range1 = ranges[1];
    let range2 = ranges[2];

    if (vl <= range1) {
        let t = (vl - range0) / (range1 - range0);
        return Math.max(0, Math.min(1, t));
    } else {
        let t = (vl - range1) / (range2 - range1);
        return Math.max(0, Math.min(1, t));
    }
}


function valToPctToColor(vl, initOpacity, elOpa, config, opaBuff=0) {

    let opacity = initOpacity;
    if (elOpa){
        opacity = elOpa.value;
        opacity = elOpa.value.toString(16);
        opacity = parseFloat(opacity);
    }

    opacity += opaBuff;
    if (opacity > 1.0) {
        opacity = 1.0;
    }
    if (opacity < 0.0) {
        opacity = 0.0;
    }

    let tmp = Math.floor(opacity * 255);
    let opacityHex = tmp.toString(16);
    if (opacityHex.length < 2) {
        opacityHex = "0" + opacityHex;
    }

    const gradWrap2 = document.getElementById("gradient1");
    if (gradWrap2) {
        gradWrap2.style.opacity = opacity;
    }


    const ranges = config["color_ranges"]
    const colors = config["colors"]  //     ["#FF0000", "#80A000", "#00A000"]

    function separateVals(hexColor) {
        let cleanHex = hexColor.replace("#", "");
        let componentArray = [];
        for (let idx1 = 0; idx1 < cleanHex.length; idx1 += 2) {
            let hexPair = cleanHex.substring(idx1, idx1 + 2);
            let comp = parseInt(hexPair, 16);
            componentArray.push(comp);
        }
        return componentArray;
    }

    let colorsSeparated = [];
    for (let [idx1, color] of colors.entries()) {
        let rgbComponents = separateVals(color);
        colorsSeparated.push(rgbComponents);
    }

    // const colR0 = [0x00, 0xA0, 0x00]; // mostly green
    // const colR1 = [0x80, 0x80, 0x00]; // yellow
    // const colR2 = [0xff, 0x00, 0x00]; // red

    const colR0 = colorsSeparated[0];
    const colR1 = colorsSeparated[1];
    const colR2 = colorsSeparated[2];


    function interpolate(a, b, t) {
        const out = [0, 0, 0];
        for (let idx1 = 0; idx1 < 3; idx1++) {
            out[idx1] = Math.round(a[idx1] + (b[idx1] - a[idx1]) * t);
        }
        return out;
    }

    let r0 = ranges[0];
    let r1 = ranges[1];
    let r2 = ranges[2];

    let rgb;

    if (vl <= r0) {
        rgb = colR0.slice();
    } else if (vl <= r1) {
        let t = mapToZeroOne(vl, ranges);
        rgb = interpolate(colR0, colR1, t);
    } else if (vl <= r2) {
        let t = mapToZeroOne(vl, ranges);
        rgb = interpolate(colR1, colR2, t);
    } else {
        rgb = colR2.slice();
    }

    const asHex = rgb.map(function (v) {
        const  h = v.toString(16);
        return h.length === 1 ? "0" + h : h;
    });

    return "#" + asHex.join("") + opacityHex;
}
// color funcs stop








function buildTicks(config, elParent, color_ranges, minValue, maxValue, fullRange) {

    // remove old ticks
    const oldTicks = elParent.querySelectorAll(".tick");
    for (let idx1 = 0; idx1 < oldTicks.length; idx1 += 1) {
        oldTicks[idx1].remove();
    }

    const tickValuesSet = new Set();

    // ticks when hue changes
    for (let idx1 = 0; idx1 < color_ranges.length; idx1 += 1) {
        // tickValuesSet.add(color_ranges[idx1]);
        // console.log(` tick  at hue boundary  ${color_ranges[idx1]}`)
    }

    // ticks depending on range size
    if (fullRange < 6) {
        // every full number
        const sttInt = Math.ceil( minValue);
        const endInt = Math.floor(maxValue);

        for (let curVal = sttInt; curVal <= endInt; curVal += 1) {
            // console.log(` tick-range-6 at ${curVal}`)
            tickValuesSet.add(curVal);
        }

    } else if (fullRange <= 10) {
        // every even number
        const sttEven = Math.ceil( minValue / 2) * 2;
        const endEven = Math.floor(maxValue / 2) * 2;

        for (let curVal = sttEven; curVal <= endEven; curVal += 2) {
            // console.log(` tick-range-10 at ${curVal}`)
            tickValuesSet.add(curVal);
        }

    } else if (fullRange <= 90) {
        // every even number
        const sttEven = Math.ceil( minValue / 20) * 20;
        const endEven = Math.floor(maxValue / 20) * 20;

        for (let curVal = sttEven; curVal <= endEven; curVal += 20) {
            // console.log(` tick-range-10 at ${curVal}`)
            tickValuesSet.add(curVal);
        }

    } else {
        // every 20% of the full range (0, 20, 40, 60, 80, 100%)

        const sttEven = Math.ceil( minValue / 50) * 50;
        const endEven = Math.floor(maxValue / 50) * 50;

        for (let curVal = sttEven; curVal <= endEven; curVal += 50) {
            // console.log(` tick-range-xx at ${curVal}`)
            tickValuesSet.add(curVal);
        }

    }

    let formatter = function(vl){
        return vl + "%";
    }
    if (config.formatter_legend) {
        formatter = config.formatter_legend;
    }

    const tickValues = Array.from(tickValuesSet).sort((a, b) => a - b);
    for (let idx1 = 0; idx1 < tickValues.length; idx1 += 1) {

        const value = tickValues[idx1];
        const positionPercent = (value - minValue) / fullRange * 100;
        if (positionPercent < 0 || positionPercent > 100) {
            continue;
        }
        const tickElement = document.createElement("div");
        tickElement.className = "tick";
        tickElement.style.left = positionPercent + "%";
        tickElement.textContent = formatter(value);
        elParent.appendChild(tickElement);
    }
}

function gradientCss(gradientElement, color_ranges, colors, minValue, maxValue, fullRange) {

    const stops = [];

    for (let idx1 = 0; idx1 < color_ranges.length; idx1 += 1) {

        const boundaryValue   = color_ranges[idx1];
        const pct = (boundaryValue - minValue) / fullRange * 100;
        const positionPercent = Math.round(pct*10)/10;

        // previous color up to boundary
        stops.push(colors[idx1] + " " + positionPercent + "%");
        // hard edge: next color starts at same position
        stops.push(colors[idx1] + " " + positionPercent + "%");
    }

    // ensure last color reaches 100%
    stops.push(colors[colors.length - 1] + " 100%");

    const gradientCss = "linear-gradient( \n\tto right, \n\t" + stops.join(", \n\t") + "\n)";
    // console.log(`background:  ${gradientCss};`)
    gradientElement.style.background = gradientCss;
}



function createGradientLegend(domEl, config) {

    const elGradient = document.getElementById(domEl);
    const elParent   = elGradient.parentElement;

    const color_ranges = config.color_ranges.slice().sort((a, b) => a - b);  // ensure ascending
    const colors       = config.colors;

    if (colors.length !== color_ranges.length) {
        console.error("colors.length must equal color_ranges.length");
        return;
    }

    const minValue  = color_ranges[0];
    const maxValue  = color_ranges[color_ranges.length - 1];
    const fullRange = maxValue - minValue;

    gradientCss(elGradient, color_ranges, colors, minValue, maxValue, fullRange);

    buildTicks(config, elParent, color_ranges, minValue, maxValue, fullRange);

}


// evaluating temporal membership status for styling and labels
// extracted to global funcs.js to prevent code duplication across templates
function getCountryDisplayProps(
    country,
    timeKey,
    vl,
    countryDates,
    config,
    initOpacity,
    elOpa,
) {


    const dates = countryDates[country];
    if (!dates) {
        console.log(` did not find ${country}`)
        return {
            status: "non-eu",
            areaColor: '#eee',
            tooltipText: country + "\n(non EU)",
            showLabel: false,
            labelText: "",
        };
    }

    if ( country === "Euro area (20 countries)") {
        console.log(` did find Euro area`)
    }

    // extracting year from timeKey (handles both YYYY and YYYY-MM)
    const currentYear = parseInt(String(timeKey).substring(0, 4), 10);

    let isEu = false;
    if (dates.euJoin) {
        const joinYear = parseInt(dates.euJoin.substring(0, 4), 10);
        if (currentYear >= joinYear) {
            isEu = true;
        }
    }
    if (dates.euLeave) {
        const leaveYear = parseInt(dates.euLeave.substring(0, 4), 10);
        if (currentYear >= leaveYear) {
            isEu = false;
        }
    }

    let isEuro = false;
    if (dates.euroJoin) {
        const joinYear = parseInt(dates.euroJoin.substring(0, 4), 10);
        if (currentYear >= joinYear) {
            isEuro = true;
        }
    }
    if (dates.euroLeave) {
        const leaveYear = parseInt(dates.euroLeave.substring(0, 4), 10);
        if (currentYear >= leaveYear) {
            isEuro = false;
        }
    }

    if (!isEu) {
        return {
            status: "non-eu",
            areaColor: '#eee',
            tooltipText: country + "\n(non EU)",
            showLabel: false,
            labelText: ""
        };
    }

    if (!isEuro) {
        let lblText = vl !== null && vl !== undefined && vl !== "" ? config.formatter(vl) : "N/A";
        return {
            status: "non-euro",
            areaColor: 'rgb(238, 245, 245)',
            tooltipText: country + "\n(no €)",
            showLabel: true,
            labelColor: '#666',
            labelText: lblText
        };
    }

    // euro
    let lblText = vl !== null && vl !== undefined && vl !== "" ? config.formatter(vl) : "N/A";
    let color   = vl !== null && vl !== undefined && vl !== "" ? valToPctToColor(vl, initOpacity, elOpa, config) : '#ccc';
    return {
        status: "euro",
        areaColor: color,
        tooltipText: country,
        showLabel: true,
        labelColor: color,
        labelText: lblText
    };
}


/**
 * keydown listener  - triggering the link backspace-home click when Backspace is pressed —
 *  exempt input fields - otherwise we break text editing
 */
document.addEventListener("keydown", function(event) {

    const activeEl   = document.activeElement;


    // alt-left should work - even if yearSlider is focussed
    if (activeEl.id === "yearSlider"){
        if (event.altKey && event.key === "ArrowLeft"){
            console.log(`alt left detected`);
            window.history.back();
            return;
        }
    }


    // backspace triggers link to home
    if (event.key === "Backspace") {
        let   isEditable = activeEl &&
            (
                activeEl.tagName === "INPUT" ||
                activeEl.tagName === "TEXTAREA" ||
                activeEl.isContentEditable
            );

        if (activeEl.id === "yearSlider"){
            isEditable = false;
        }
        if (isEditable === false) {
            event.preventDefault();
            const lnkBksp = document.getElementById("backspace-home");
            if (lnkBksp) {
                // console.log(`page keydown -  isEditable ${isEditable}`)
                lnkBksp.click();
            }
        }
    }


});