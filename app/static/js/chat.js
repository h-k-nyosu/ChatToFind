export function sendUserMessage(message) {
  responseAiMessage(message);
}

const chatMessages = document.getElementById("chat-messages");

function createMessageComponent(user, imgSrc, messageText) {
  const messageContainer = document.createElement("div");
  messageContainer.classList.add(user + "-message-container");

  const messageAvatar = document.createElement("div");
  messageAvatar.classList.add(user + "-message-avatar");
  const avatarImg = document.createElement("img");
  avatarImg.src = imgSrc;
  avatarImg.alt = user + " avatar";
  messageAvatar.appendChild(avatarImg);

  const messageContent = document.createElement("div");
  messageContent.classList.add(user + "-message-content");
  const messageP = document.createElement("p");
  messageP.innerText = messageText;
  messageContent.appendChild(messageP);

  messageContainer.appendChild(messageAvatar);
  messageContainer.appendChild(messageContent);

  return messageContainer;
}

function responseAiMessage(message) {
  if (message.trim() === "END") {
    return;
  }

  const userMessage = createMessageComponent(
    "user",
    "https://cdn-icons-png.flaticon.com/512/1077/1077114.png",
    message
  );
  chatMessages.appendChild(userMessage);

  const aiMessage = createMessageComponent(
    "ai",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/1200px-ChatGPT_logo.svg.png",
    ""
  );
  chatMessages.appendChild(aiMessage);

  const source = new EventSource(
    `/question-stream?message=${encodeURIComponent(message)}`
  );
  console.log("question-stream start");

  source.onmessage = function (event) {
    const aiMessageP = aiMessage.querySelector("p");

    if (event.data.trim() === "END") {
      source.close();
      console.log("question-stream finish");
    } else {
      console.log("aiMessageP: " + `${event.data}`);
      aiMessageP.innerText += `${event.data}`;
      scrollToBottom();
      console.log("chatMessages.append(" + `${event.data}` + ")");
    }
  };
}

function scrollToBottom() {
  const chatMessages = document.querySelector(".chat-messages");
  chatMessages.scrollTop = chatMessages.scrollHeight;
}
