async function loadBookmarks() {
  const res = await fetch("/api/bookmarks");
  const data = await res.json();
  const list = document.getElementById("list");
  list.innerHTML = "";
  for (const [collection, items] of Object.entries(data.collections)) {
    list.innerHTML += `<h2>📂 ${collection}</h2>`;
    items.forEach(b => {
      list.innerHTML += `<div class="card"><a href="${b.url}" target="_blank">${b.title}</a><div>${b.tags.join(", ")}</div></div>`;
    });
  }
}
function openBrowser() {
  window.open(window.location.href, "_blank");
}
async function addBookmark() {
  const title = titleEl.value;
  const url = urlEl.value;
  const tags = tagsEl.value.split(",");
  await fetch("/api/bookmarks", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({title, url, tags})
  });
  loadBookmarks();
}
const titleEl = document.getElementById("title");
const urlEl = document.getElementById("url");
const tagsEl = document.getElementById("tags");
loadBookmarks();