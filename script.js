// Function to show the login form and hide the signup form
function showLogin() {
    document.getElementById('login').style.display = 'block';
    document.getElementById('signup').style.display = 'none';
}

// Function to show the signup form and hide the login form
function showSignup() {
    document.getElementById('login').style.display = 'none';
    document.getElementById('signup').style.display = 'block';
}

// Function to validate login form
function validateLogin() {
    let email = document.getElementById("login-email").value.trim();
    let password = document.getElementById("login-password").value.trim();
    let emailError = document.getElementById("email-error");
    let passwordError = document.getElementById("password-error");

    let valid = true;

    // Email format validation using regex
    let emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!email) {
        emailError.innerText = "Email field cannot be empty";
        emailError.style.color = "red";
        valid = false;
    } else if (!emailPattern.test(email)) {
        emailError.innerText = "Please enter a valid email address";
        emailError.style.color = "red";
        valid = false;
    } else {
        emailError.innerText = ""; // Clear error if valid
    }

    // Password validation (Minimum 6 characters)
    if (!password) {
        passwordError.innerText = "Password field cannot be empty";
        passwordError.style.color = "red";
        valid = false;
    } else if (password.length < 6) {
        passwordError.innerText = "Password must be at least 6 characters long";
        passwordError.style.color = "red";
        valid = false;
    } else {
        passwordError.innerText = ""; // Clear error if valid
    }

    return valid; // Prevent form submission if invalid
}

// Real-time validation for email and password fields
document.getElementById("login-email").addEventListener("input", function () {
    let emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    let emailError = document.getElementById("email-error");
    if (this.value.trim() === "") {
        emailError.innerText = "Email field cannot be empty";
        emailError.style.color = "red";
    } else if (!emailPattern.test(this.value)) {
        emailError.innerText = "Please enter a valid email address";
        emailError.style.color = "red";
    } else {
        emailError.innerText = "";
    }
});

document.getElementById("login-password").addEventListener("input", function () {
    let passwordError = document.getElementById("password-error");
    if (this.value.trim() === "") {
        passwordError.innerText = "Password field cannot be empty";
        passwordError.style.color = "red";
    } else if (this.value.length < 6) {
        passwordError.innerText = "Password must be at least 6 characters long";
        passwordError.style.color = "red";
    } else {
        passwordError.innerText = "";
    }
});

// Attach validation to login form submission
document.addEventListener("DOMContentLoaded", function () {
    let loginForm = document.getElementById("login");
    if (loginForm) {
        loginForm.onsubmit = function () {
            return validateLogin();
        };
    }
});
