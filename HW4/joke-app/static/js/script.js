// Replace the entire contents of static/js/script.js with this updated version

document.addEventListener("DOMContentLoaded", () => {
  const jokeContainer = document.getElementById("joke-container");
  const loadingIndicator = document.getElementById("loading");
  const currentUsername = document.body.dataset.username; // Get username from body data attribute
  let isLoading = false;

  const fetchJoke = async () => {
    if (isLoading) return;
    isLoading = true;
    loadingIndicator.style.display = "block";

    try {
      const response = await fetch("/api/jokes");
      const joke = await response.json();

      if (joke && joke.content) {
        // --- Create the joke card ---
        const jokeCard = document.createElement("div");
        jokeCard.className = "joke-card";

        const jokeParagraph = document.createElement("p");
        jokeParagraph.style.whiteSpace = "pre-wrap";
        jokeParagraph.textContent = joke.content;

        const jokeAuthorSmall = document.createElement("small");
        jokeAuthorSmall.textContent = "- Posted by "; // Text before the link

        const authorLink = document.createElement("a");
        authorLink.className = "author-link";
        authorLink.href = `/user/${joke.author_username}`;
        authorLink.textContent = joke.author_username;

        jokeAuthorSmall.appendChild(authorLink);

        jokeCard.appendChild(jokeParagraph);
        jokeCard.appendChild(jokeAuthorSmall);

        // --- NEW: Add edit/delete controls if user is the author ---
        if (currentUsername && joke.author_username === currentUsername) {
          const controlsDiv = document.createElement("div");
          controlsDiv.className = "joke-controls";

          // Edit link
          const editLink = document.createElement("a");
          editLink.href = `/edit_joke/${joke._id}`;
          editLink.className = "edit-link";
          editLink.textContent = "Edit";

          // Delete form and button
          const deleteForm = document.createElement("form");
          deleteForm.action = `/delete_joke/${joke._id}`;
          deleteForm.method = "POST";
          deleteForm.onsubmit = () =>
            confirm("Are you sure you want to delete this joke?");

          const deleteButton = document.createElement("button");
          deleteButton.type = "submit";
          deleteButton.className = "delete-button";
          deleteButton.textContent = "Delete";

          deleteForm.appendChild(deleteButton);
          controlsDiv.appendChild(editLink);
          controlsDiv.appendChild(deleteForm);

          jokeCard.appendChild(controlsDiv);
        }

        jokeContainer.appendChild(jokeCard);
      }
    } catch (error) {
      console.error("Failed to fetch a new joke:", error);
    } finally {
      loadingIndicator.style.display = "none";
      isLoading = false;
    }
  };

  window.addEventListener("scroll", () => {
    if (
      window.innerHeight + window.scrollY >=
      document.body.offsetHeight - 100
    ) {
      fetchJoke();
    }
  });
});
