const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");

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
  console.log("question-stream start");
  source.onmessage = function (event) {
    if (event.data.trim() === "END") {
      source.close(); // メッセージが完了したらEventSourceを閉じる
      console.log("question-stream finish");
    } else {
      console.log("aiMessageP: " + `${event.data}`);
      aiMessageP.innerText += `${event.data}`;
      chatMessages.appendChild(aiMessageContainer);
      scrollToBottom();
      console.log("chatMessages.append(" + `${event.data}` + ")");
    }
  };
}

function renderItem(job) {
  return `
        <a href="/jobs/${job.id}">
          <div class="item">
            <p class="item-job-type">#${job.job_type}</p>
            <h3 class="item-job-title">${job.title}</h3>
            <p class="item-job-monthly-salary">月給：${job.monthly_salary}円</p>
            <p class="item-job-location">勤務地：${job.location}</p>
          </div>
        </a>
      `;
}

function renderSearchResult(searchResult) {
  if (searchResult.search_results.length === 0) {
    return "";
  }

  const searchResultItems = searchResult.search_results
    .map(renderItem)
    .join("");

  return `
        <h2 class="search-title">${searchResult.title}</h2>
        <div class="search-results">
          ${searchResultItems}
        </div>
      `;
}

function renderMainContent(searchResults) {
  const mainContent = document.querySelector(".main-content");
  mainContent.innerHTML = searchResults.map(renderSearchResult).join("");
}

function fetchSearchItems(message) {
  console.log("fetchSearchItems start");
  fetch(`/search-items?message=${encodeURIComponent(message)}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Error fetching search items");
      }
      return response.json();
    })
    .then((searchResults) => {
      console.log(searchResults);
      console.log("searchResults.title: " + searchResults.title);
      console.log(
        "searchResults.search_results: " + searchResults.search_results
      );
      console.log("fetchSearchItems finish");
      renderMainContent(searchResults);
    })
    .catch((error) => {
      console.error(error);
    });
}

function sendUserMessage(message) {
  responseAiMessage(message);
  fetchSearchItems(message);
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  sendUserMessage(chatInput.value);
  chatInput.value = "";
});

function scrollToBottom() {
  const chatMessages = document.querySelector(".chat-messages");
  chatMessages.scrollTop = chatMessages.scrollHeight;
}
