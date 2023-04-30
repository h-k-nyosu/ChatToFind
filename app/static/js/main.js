import { sendUserMessage } from "./chat.js";
import { fetchSearchItems } from "./search.js";

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  sendUserMessage(chatInput.value);
  fetchSearchItems(chatInput.value);
  chatInput.value = "";
});
