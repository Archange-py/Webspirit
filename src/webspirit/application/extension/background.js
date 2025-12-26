// background.js
// Fonction d'envoi du bookmark au serveur local
function sendBookmark(url, title) {
    fetch("http://127.0.0.1:8000/api/bookmarks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url, title: title })
    })
        .then(response => {
            if (!response.ok) {
                console.error("Erreur lors de l'envoi du bookmark:",
                    response.statusText);
            }
        })
        .catch(err => console.error("Erreur réseau:", err));
}
// Récupère l'onglet actif et envoie ses infos
function captureActiveTab() {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        const tab = tabs[0];
        if (tab && tab.url && tab.title) {
            sendBookmark(tab.url, tab.title);
            console.log("Bookmark capturé:", tab.title, tab.url);
        }
    });
}
// Événement clic sur l'icône de l'extension
chrome.browserAction.onClicked.addListener(captureActiveTab);
// Événement raccourci clavier
chrome.commands.onCommand.addListener(function (command) {
    if (command === "capture") {
        captureActiveTab();
    }
});