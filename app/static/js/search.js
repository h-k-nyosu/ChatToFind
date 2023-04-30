export function fetchSearchItems(message) {
  console.log("fetchSearchItems start");
  fetch(`/search-items?message=${encodeURIComponent(message)}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Error fetching search items");
      }
      return response.json();
    })
    .then((searchResults) => {
      renderMainContent(searchResults);
    })
    .catch((error) => {
      console.error(error);
    });
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