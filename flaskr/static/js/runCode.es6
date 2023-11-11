const run_code_of_conversation_endpoint = document.currentScript.getAttribute('run-code-of-conversation-endpoint')
const loadingImageFileName = document.currentScript.getAttribute('loading-image-file-name')

let isDeploying = false
let retries = 0
const MAX_RETRIES = 5

function runCodeOfConversation(buttonEl, conversationId) {
    if (isDeploying) return;
    isDeploying = true
    buttonEl.querySelector('.deploying').classList.remove('hide')
    buttonEl.querySelector('.default').classList.add('hide')
    document.querySelectorAll('.run-code').forEach(el => el.disabled = true)

    document.body.classList.add("deploying")
    if (!document.getElementById('modal-run-code-overlay')) {
        document.body.insertAdjacentHTML('beforeend',
            `<div id="modal-run-code-overlay" class="modal-overlay">
  <div class="modal flex flex-column">
    <header class="flex">
        <h3 class="mb0 underline">Lichteffekt wird übertragen</h3>
        <button id="close-modal" class="btn ml-auto">X</button>
    </header>
    <p class="message success">Es hat geklappt; die Lichterkette sollte jeden Moment leuchten.</p>
    <p class="message deploying">
    Jetzt wird der Programmcode auf die Lichterkette übertragen und ist gleich zu sehen.
    <img class="loading ml1" src="${loadingImageFileName}" alt="Bitte warten" width="42px" class="ml1">
    </p>
    <p class="message error">
    Beim Übertragen auf die Lichterkette trat ein Fehler auf. Das passiert manchmal, deswegen versuche ich es erneut.
    <img class="loading ml1" src="${loadingImageFileName}" alt="Bitte warten" width="42px" class="ml1">
    </p>
    <p class="message error-no-retry">Das hat nicht geklappt! Sag im Chat Bescheid, dass der Programmcode nicht funktioniert.
    </p>
    <p class="actions error-no-retry flex justify-end">
        <button onclick="setDescriptionToError()" class="btn ml1">Problem im Chat mitteilen</button>
    </p>
  </div>
</div>`)
        document.getElementById('close-modal').addEventListener('click', () => {
            document.getElementById('modal-run-code-overlay').remove()
            document.body.classList.remove("deployment-failed-no-retry")
        })
    }

    fetch(run_code_of_conversation_endpoint.replace('conversation-id-placeholder', conversationId), {
        method: 'POST'
    }).then(async response => {
        isDeploying = false
        if (!response.ok) {
            throw new Error(`Request failed: ${await response.text()}`);
        }
        if (retries > 0) {
            document.body.classList.remove("deployment-failed")
            retries = 0
        }
        document.body.classList.add("deployed-successfully")
        setTimeout(() => {
            document.body.classList.remove("deployed-successfully")
            document.getElementById("modal-run-code-overlay")?.remove()
        }, 3000)
    })
        .catch(error => {
            console.error('Error while deploying code: ', error);
            buttonEl.classList.replace('success', 'alert')
            buttonEl.querySelector('.errored').classList.remove('hide')
            if (retries < MAX_RETRIES) {
                document.body.classList.add("deployment-failed")
                setTimeout(() => {
                    buttonEl.classList.replace('alert', 'success')
                    buttonEl.querySelector('.errored').classList.add('hide')
                }, 5000)
                retries++;
                runCodeOfConversation(buttonEl, conversationId)
            } else {
                document.body.classList.remove("deployment-failed")
                document.body.classList.add("deployment-failed-no-retry")
                setTimeout(() => {
                    buttonEl.classList.replace('alert', 'success')
                    buttonEl.querySelector('.errored').classList.add('hide')
                }, 5000)
                retries = 0
            }
        }).finally(() => {
        document.body.classList.remove("deploying")
        buttonEl.querySelector('.default').classList.remove('hide')
        buttonEl.querySelector('.deploying').classList.add('hide')
        document.querySelectorAll('.run-code').forEach(el => el.disabled = false)
    });
}

function setDescriptionToError() {
    document.getElementById("close-modal").click()
    document.getElementById("description-input").value = "Der Programmcode kann nicht ausgeführt werden. Suche und behebe Programmfehler."
}
