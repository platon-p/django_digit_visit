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
    };
}
const copy_btns = document.querySelectorAll('.copy_btn')
copy_btns.forEach(function (elem) {
        elem.onclick = function () {
            navigator.clipboard.writeText(elem.getAttribute('content'))
            elem.innerText = 'Скопировано'
            elem.style.color = '#1aaf1a'
            setTimeout(function () {
                elem.innerText = 'Скопировать адрес'
                elem.style.color = '#ccc'
            }, (2 * 1000))
        }
    }
)