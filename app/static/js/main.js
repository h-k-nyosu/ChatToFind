import { sendUserMessage } from "./chat.js";
import { fetchSearchItems } from "./search.js";

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const submitButton = document.getElementById("submit-button");

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (chatInput.value !== "") {
    const userMessage = chatInput.value;
    submitButton.disabled = true;
    chatInput.value = "";
    const aiMessage = await sendUserMessage(userMessage);

    await fetchSearchItems(aiMessage);
    submitButton.disabled = false;
    console.log("main finish");
  }
});
