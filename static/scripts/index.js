function showAnswer(elemId) {
    let elem = document.getElementById('answer' + elemId);
    let plus = document.getElementById('question' + elemId);
    elem.style.display = elem.style.display === "none" ? 'block' : 'none';
    plus.style.transform = plus.style.transform === "" ? "rotate(135deg)" : "";
}