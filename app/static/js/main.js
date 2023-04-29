const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  sendUserMessage(chatInput.value, true);
  chatInput.value = "";
});

function responseAiMessage(message) {
  // メッセージが空の場合、何もしない
  if (message.trim() === "END") {
    return;
  }

  // ユーザーメッセージコンポーネントの作成
  const userMessageContainer = document.createElement("div");
  userMessageContainer.classList.add("user-message-container");

  const userMessageAvatar = document.createElement("div");
  userMessageAvatar.classList.add("user-message-avatar");
  const userAvatarImg = document.createElement("img");
  userAvatarImg.src = "https://cdn-icons-png.flaticon.com/512/1077/1077114.png";
  userAvatarImg.alt = "user avatar";
  userMessageAvatar.appendChild(userAvatarImg);

  const userMessageContent = document.createElement("div");
  userMessageContent.classList.add("user-message-content");
  const userMessageP = document.createElement("p");
  userMessageP.innerText = message;
  userMessageContent.appendChild(userMessageP);

  userMessageContainer.appendChild(userMessageAvatar);
  userMessageContainer.appendChild(userMessageContent);

  chatMessages.appendChild(userMessageContainer);

  // AIメッセージコンポーネントの作成
  const aiMessageContainer = document.createElement("div");
  aiMessageContainer.classList.add("ai-message-container");

  const aiMessageAvatar = document.createElement("div");
  aiMessageAvatar.classList.add("ai-message-avatar");
  const aiAvatarImg = document.createElement("img");
  aiAvatarImg.src =
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/1200px-ChatGPT_logo.svg.png";
  aiAvatarImg.alt = "ai avatar";
  aiMessageAvatar.appendChild(aiAvatarImg);

  const aiMessageContent = document.createElement("div");
  aiMessageContent.classList.add("ai-message-content");
  const aiMessageP = document.createElement("p");
  aiMessageP.innerText = "";
  aiMessageContent.appendChild(aiMessageP);

  aiMessageContainer.appendChild(aiMessageAvatar);
  aiMessageContainer.appendChild(aiMessageContent);

  chatMessages.appendChild(aiMessageContainer);

  // ここでストリーミングレスポンスを受信するための EventSource を作成
  const source = new EventSource(
    `/question-stream?message=${encodeURIComponent(message)}`
  );

  source.onmessage = function (event) {
    if (event.data.trim() === "END") {
      source.close(); // メッセージが完了したらEventSourceを閉じる
    } else {
      aiMessageP.innerText += `${event.data}`;
      chatMessages.appendChild(aiMessageContainer);
    }
  };
}

function fetchSearchItems(message) {
  fetch(`/search-items?message=${encodeURIComponent(message)}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Error fetching search items");
      }
      return response.json();
    })
    .then((searchResults) => {
      console.log(searchResults);
    })
    .catch((error) => {
      console.error(error);
    });
}

function sendUserMessage(message) {
  responseAiMessage(message);
  fetchSearchItems(message);
}
