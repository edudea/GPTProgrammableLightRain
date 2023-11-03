let chatContainer = document.querySelector(".chat-panels-container")
let scrollToFirstBtn = document.querySelector(".scroll-to-first")
let scrollToLastBtn = document.querySelector(".scroll-to-last")

function scrollChatTo(y) {
    chatContainer.scroll({
        top: y,
        left: 0,
        behavior: "smooth",
    });
}

scrollToFirstMessage = () => scrollChatTo(0)
scrollToLastMessage = () => scrollChatTo(chatContainer.scrollHeight)

function adaptButtonsToScrollState() {
    if (chatContainer.scrollHeight < chatContainer.clientHeight + 420) {
        scrollToFirstBtn.classList.add("display-none")
        scrollToLastBtn.classList.add("display-none")
    } else if (chatContainer.scrollTop < 100) {
        scrollToFirstBtn.classList.add("display-none")
        scrollToLastBtn.classList.remove("display-none")
    } else if (chatContainer.scrollTop > chatContainer.scrollHeight - chatContainer.clientHeight - 420) {
        scrollToFirstBtn.classList.remove("display-none")
        scrollToLastBtn.classList.add("display-none")
    } else {
        scrollToFirstBtn.classList.add("display-none")
        scrollToLastBtn.classList.add("display-none")
    }
}

chatContainer.onscroll = function () {
    adaptButtonsToScrollState();
}
scrollToLastMessage()
adaptButtonsToScrollState();