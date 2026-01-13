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

