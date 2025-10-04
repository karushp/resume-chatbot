async function sendMessage() {
    const input = document.getElementById("userInput").value;
    const chat = document.getElementById("chat");
  
    chat.innerHTML += `<p><b>You:</b> ${input}</p>`;
  
    const response = await fetch("https://your-backend.onrender.com/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: input })
    });
  
    const data = await response.json();
    chat.innerHTML += `<p><b>Bot:</b> ${data.answer}</p>`;
  }