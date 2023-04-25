document.getElementById("chat-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (message) {
    addMessage(message);
    input.value = "";
  }
});

function addMessage(message) {
  const messages = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.innerText = message;
  messages.appendChild(div);
}
