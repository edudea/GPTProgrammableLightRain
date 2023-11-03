document.querySelectorAll(".chat-text").forEach(chatElement => {
    const regex = /(?<before>.*)\n```.{0,4}\n(?<code>.*)\n```\n(?<after>.*)/s;
    const conversationId = chatElement.parentElement.getAttribute("data-conversation-id")

    const htmlReplacement = {
        tagopen: `<div class="border panel source-code flex flex-column">
                            <div class="code-action-buttons flex">
                                <button class="btn success run-code" onclick="runCodeOfConversation(this, '${conversationId}')">
                                    <div class="default">Ausführen <img class="ml1" src="${document.currentScript.getAttribute('execute-image-file-name')}" alt="Auf Lichtstreifen abspielen" width="20px" class="ml1"></div>
                                    <div class="deploying hide">Wird installiert <img class="loading ml1" src="${document.currentScript.getAttribute('loading-image-file-name')}" alt="Bitte warten" width="20px" class="ml1"></div>
                                    <div class="errored hide">Installation fehlgeschlagen</div>
                                </button>
                            </div>
                            <pre><code class="language-cpp">`,
        tagclose: "</code></pre></div>"
    };
    chatElement.innerHTML = chatElement.innerHTML.replace(regex, (match, before, code, after) => {
        return before + htmlReplacement.tagopen + code + htmlReplacement.tagclose + after;
    });
})
hljs.highlightAll();


const run_code_of_conversation_endpoint = document.currentScript.getAttribute('run-code-of-conversation-endpoint')

let isDeploying = false
function runCodeOfConversation($this, conversationId) {
    if (isDeploying) return;
    isDeploying = true
    $this.querySelector('.deploying').classList.remove('hide')
    $this.querySelector('.default').classList.add('hide')
    document.querySelectorAll('.run-code').forEach(el => el.disabled = true)
    fetch(run_code_of_conversation_endpoint.replace('conversation-id-placeholder', conversationId), {
        method: 'POST'
    }).then(async response => {
        if (!response.ok) {
            throw new Error(`Netzwerkantwort war nicht ok: ${await response.text()}`);
        }
    })
        .catch(error => {
            console.error('Fehler beim Senden des Requests:', error);
            $this.classList.replace('success', 'alert')
            $this.querySelector('.errored').classList.remove('hide')
            setTimeout(() => {
                $this.querySelector('.errored').classList.add('hide')
                $this.classList.replace('alert', 'success')
            }, 5000)
        }).finally(() => {
        $this.querySelector('.default').classList.remove('hide')
        $this.querySelector('.deploying').classList.add('hide')
        document.querySelectorAll('.run-code').forEach(el => el.disabled = false)
        isDeploying = false
    });
}
const style = document.createElement('style')
style.innerHTML = `
.run-code.alert .default, .run-code.alert .deploying {
    display: none !important;
}
`
document.body.appendChild(style)
