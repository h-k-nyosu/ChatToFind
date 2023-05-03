import { sendUserMessage } from "./chat.js";
import { fetchSearchItems } from "./search.js";

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const submitButton = document.getElementById("submit-button");
const sessionId = document.getElementById("session-id").value;

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (chatInput.value !== "") {
    const userMessage = chatInput.value;
    submitButton.disabled = true;
    chatInput.value = "";
    const aiMessage = await sendUserMessage(userMessage, sessionId);

    await fetchSearchItems(aiMessage);
    submitButton.disabled = false;
    console.log("main finish");
  }
});
