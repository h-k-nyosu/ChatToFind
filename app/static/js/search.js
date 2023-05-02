export async function fetchSearchItems(message) {
  console.log("fetchSearchItems start");
  try {
    const response = await fetch(
      `/search-items?message=${encodeURIComponent(message)}`
    );

    if (!response.ok) {
      throw new Error("Error fetching search items");
    }

    const searchResults = await response.json();
    renderMainContent(searchResults);
  } catch (error) {
    console.error(error);
  }
}

function renderItem(job) {
  return `
        <a href="/jobs/${job.id}" target="_blank" rel="noopener noreferrer">
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
