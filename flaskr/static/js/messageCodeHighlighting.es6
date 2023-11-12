(() => {
    const executeImageFileName = document.currentScript.getAttribute('execute-image-file-name')
    const loadingImageFileName = document.currentScript.getAttribute('loading-image-file-name')
    const findAndReplaceCodeBlock = chatElement => {
        const regex = /(?<before>.*)\n```.{0,10}\n(?<code>.*)\n```\n(?<after>.*)/s;
        const conversationId = chatElement.parentElement.getAttribute("data-conversation-id")

        const htmlReplacement = {
            tagopen: `<div class="border panel source-code flex flex-column my1">
                            <div class="code-action-buttons flex">
                                <button class="btn success run-code" onclick="runCodeOfConversation(this, '${conversationId}')">
                                    <div class="default">Ausführen <img class="ml1" src="${executeImageFileName}" alt="Auf Lichtstreifen abspielen" width="20px" class="ml1"></div>
                                    <div class="deploying hide">Wird installiert <img class="loading ml1" src="${loadingImageFileName}" alt="Bitte warten" width="20px" class="ml1"></div>
                                    <div class="errored hide">Installation fehlgeschlagen</div>
                                </button>
                            </div>
                            <pre class="px2"><code>`,
            tagclose: "</code></pre></div>"
        };
        chatElement.innerHTML = chatElement.innerHTML.replace(regex, (match, before, code, after) => {
            return before + htmlReplacement.tagopen + hljs.highlight(code, {language: 'cpp'}).value + htmlReplacement.tagclose + after;
        });
    };

//document.querySelectorAll('.chat-text').forEach(findAndReplaceCodeBlock)

    function callback(mutationList, observer) {
        mutationList.forEach((mutation) => {
            mutation.addedNodes?.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    if (node.matches('.chat-text')) {
                        findAndReplaceCodeBlock(node)
                    } else if (node.querySelector('.chat-text')) {
                        findAndReplaceCodeBlock(node.querySelector('.chat-text'))
                    }
                }
            });
        });
    }

    const observer = new MutationObserver(callback);
    observer.observe(document.body, {childList: true, subtree: true, attributes: false, characterData: false});
    hljs.highlightAll();


    document.body.insertAdjacentHTML('beforeend', `<style>
.run-code.alert .default, .run-code.alert .deploying {
    display: none !important;
}
</style>`)
})()