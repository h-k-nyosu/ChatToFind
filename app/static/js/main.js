import { sendUserMessage } from "./chat.js";
import { fetchSearchItems } from "./search.js";

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const submitButton = document.getElementById("submit-button");

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  submitButton.disabled = true;
  sendUserMessage(chatInput.value);
  await fetchSearchItems(chatInput.value);
  submitButton.disabled = false;
  chatInput.value = "";
});
