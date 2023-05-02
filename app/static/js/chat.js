export function sendUserMessage(message) {
  const response = responseAiMessage(message);
  return response;
}

const chatMessages = document.getElementById("chat-messages");

function createMessageComponent(user, imgSrc, messageText) {
  const messageContainer = document.createElement("div");
  messageContainer.classList.add(user + "-message-container");

  const messageAvatar = document.createElement("div");
  messageAvatar.classList.add(user + "-message-avatar");
  const avatarImg = document.createElement("img");
  avatarImg.classList.add(user + "-icon-avatar");
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
    "/static/images/thinking.svg",
    message
  );
  chatMessages.appendChild(userMessage);

  const aiMessage = createMessageComponent("ai", "/static/images/star.svg", "");
  chatMessages.appendChild(aiMessage);

  const source = new EventSource(
    `/question-stream?message=${encodeURIComponent(message)}`
  );
  console.log("question-stream start");

  // Promiseを返すように変更
  return new Promise((resolve) => {
    source.onmessage = function (event) {
      const aiMessageP = aiMessage.querySelector("p");

      if (event.data.trim() === "END") {
        source.close();
        console.log("question-stream finish");
        displayLoadingIcon();
        resolve(aiMessageP.innerText);
      } else {
        aiMessageP.innerText += `${event.data}`;
        scrollToBottom();
      }
    };
  });
}

function scrollToBottom() {
  const chatMessages = document.querySelector(".chat-messages");
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function displayLoadingIcon() {
  const chatMessages = document.getElementById("chat-messages");
  const loadingIcon = document.createElement("div");
  loadingIcon.innerHTML = `
    <img
      src="/static/images/loading.gif"
      alt="Loading"
      class="loading-icon"
    />
  `;
  chatMessages.appendChild(loadingIcon);
}
