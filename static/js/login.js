document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();
  
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
  
    try {
      const response = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
  
      const result = await response.json();
      const message = document.getElementById("message");
      message.textContent = result.message;
      message.style.color = result.success ? "green" : "red";
    } catch (err) {
      console.error("Error:", err);
    }
  });
  