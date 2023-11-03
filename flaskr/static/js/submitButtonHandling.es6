// enable chat button on input
function activateSubmitButton() {
    if (document.getElementById("description-input").textLength > 0) {
        document.getElementById("edit-description-btn").removeAttribute("disabled")
    } else {
        document.getElementById("edit-description-btn").disabled = true
    }
}

document.getElementById("description-input").onkeyup = activateSubmitButton
document.getElementById("description-input").onchange = activateSubmitButton
// animate chat placeholder with different examples
let exampleInput = ["Lass die Lichterkette Marienkäfer-Rot leuchten...",
    "Ein Pixel soll wie ein Ball auf und ab hüpfen...",
    "Die Lichter sollen wie ein Kaminfeuer flackern...",
    "Lasse es wie ein Feuerwerk aussehen. Raketen sollen aufsteigen und bunt, schimmernd explodieren.",
    "Erstelle einen möglichst ausgefallenen, aber ruhigen Effekt..."]

function typewriter(elementID, texte, textIndex, n) {
    if (n < texte[textIndex].length) {
        document.getElementById(elementID).placeholder += texte[textIndex].charAt(n);
        setTimeout(function () {
            typewriter(elementID, texte, textIndex, ++n);
        }, 100);
    } else {
        textIndex = textIndex + 1 < texte.length ? textIndex + 1 : 0;
        setTimeout(function () {
            eraser(elementID, n)
            setTimeout(function () {
                typewriter(elementID, texte, textIndex, 0);
            }, n * 10 + 200)
        }, 1500);
    }
}

function eraser(elementID, n) {
    if (n > 0) {
        document.getElementById(elementID).placeholder = document.getElementById(elementID).placeholder.slice(0, -1);
        setTimeout(function () {
            eraser(elementID, --n);
        }, 10);
    }
}

document.getElementById('description-input').placeholder += "\n"
exampleInput.sort(() => Math.random() - 0.5);
typewriter('description-input', exampleInput, 0, 0)