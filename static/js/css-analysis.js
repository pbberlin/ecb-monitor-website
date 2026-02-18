function getUsedClasses() {
    const usedClasses = new Set()
    const allElements = document.querySelectorAll("*")
    for (const myElement of allElements) {
        for (const myClass of myElement.classList) {
            usedClasses.add(myClass)
        }
    }
    return usedClasses
}


function getDefinedClasses() {
    const definedClasses = new Set()
    const styleSheets = document.styleSheets
    for (let idx1 = 0; idx1 < styleSheets.length; idx1++) {
        const mySheet = styleSheets[idx1]
        let rules
        try {
            rules = mySheet.cssRules
        }
        catch (myException) {
            console.log("Cannot access stylesheet:", mySheet.href)
            console.log(myException)
            continue
        }
        for (let idx2 = 0; idx2 < rules.length; idx2++) {
            const myRule = rules[idx2]
            if (!myRule.selectorText) {
                continue
            }
            const matches = myRule.selectorText.match(/\.([a-zA-Z0-9_-]+)/g)
            if (!matches) {
                continue
            }
            for (let idx3 = 0; idx3 < matches.length; idx3++) {
                const myClass = matches[idx3].substring(1)
                definedClasses.add(myClass)
            }
        }
    }
    return definedClasses
}



function findMissingClasses() {
    const usedClasses = getUsedClasses()
    const definedClasses = getDefinedClasses()

    // console.log(definedClasses)
    // console.log(usedClasses)


    const missingClasses = []
    for (const myClass of usedClasses) {
        if (!definedClasses.has(myClass)) {
            missingClasses.push(myClass)
        }
    }
    return missingClasses
}


const missingClasses = findMissingClasses()

console.log("Classes used but not defined:")
console.log(missingClasses)
