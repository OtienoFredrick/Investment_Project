document.getElementById("forgotPasswordForm").addEventListener("submit", function(event) {
    var email = document.getElementById("email").value;
    
    if (!email) {
        alert('Please enter your email address.');
        event.preventDefault(); // Prevent form submission
    }
});
