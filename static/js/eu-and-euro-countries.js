// 27 countries
const euCountries = [
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Ireland",
    "Italy",
    "Latvia",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Poland",
    "Portugal",
    "Romania",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden"
];



// November 2025 - 20 euro countries - plus Bulgaria imminent
const euCountriesEuro = [
    "Euro area (19 countries)",  // key for ameco and eurostat
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Ireland",
    "Italy",
    "Latvia",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Portugal",
    "Slovakia",
    "Slovenia",
    "Spain"
];


const nonMembers = [
    "Norway",
    "Switzerland",
    "United Kingdom",
    "Andorra",
    "Ukraine",
    "Moldova",
    "Belarus",
    "Bosnia and Herzegovina",
    "Albania",
    "Montenegro",
    "Macedonia",
    "Serbia",
];


const euroSet = new Set(euCountriesEuro);

const notInEuro = euCountries.filter(country => !euroSet.has(country));

// console.log(notInEuro);