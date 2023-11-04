let htmlElement = document.querySelector("html")
let scrollToFirstBtn = document.querySelector(".scroll-to-first")
let scrollToLastBtn = document.querySelector(".scroll-to-last")

function scrollChatTo(y) {
    window.scroll({
        top: y,
        left: 0,
        behavior: "smooth",
    });
}

scrollToFirstMessage = () => scrollChatTo(0)
scrollToLastMessage = () => scrollChatTo(document.body.scrollHeight)

function adaptButtonsToScrollState() {
    if (document.body.scrollHeight < window.innerHeight + 420) {
        scrollToFirstBtn.classList.add("display-none")
        scrollToLastBtn.classList.add("display-none")
    } else if (htmlElement.scrollTop > document.body.scrollHeight - window.innerHeight - 420) {
        scrollToFirstBtn.classList.remove("display-none")
        scrollToLastBtn.classList.add("display-none")
    } else if (htmlElement.scrollTop < document.body.scrollHeight * .75) {
        scrollToFirstBtn.classList.add("display-none")
        scrollToLastBtn.classList.remove("display-none")
    } else {
        scrollToFirstBtn.classList.add("display-none")
        scrollToLastBtn.classList.add("display-none")
    }
}

window.onscroll = function () {
    adaptButtonsToScrollState();
}
scrollToLastMessage()
adaptButtonsToScrollState();