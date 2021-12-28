function showAnswer(elemId) {
    let elem = document.getElementById('answer' + elemId);
    let plus = document.getElementById('question' + elemId);
    elem.style.display = elem.style.display === "none" ? 'block' : 'none';
    plus.style.transform = plus.style.transform === "" ? "rotate(135deg)" : "";
}

let elem = document.getElementById('address');
if (elem) {
    elem.oninput = function () {
        document.getElementById('or').innerHTML = elem.value;
        console.log('asd')
    };
}
const copy_btn = document.getElementById('copy_btn');
copy_btn.onclick = function () {
    navigator.clipboard.writeText(copy_btn.getAttribute('content'))
    copy_btn.innerText = 'Скопировано'
    copy_btn.style.color = '#1aaf1a'
}