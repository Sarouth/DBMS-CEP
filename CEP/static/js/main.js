// main.js 
 
 
document.addEventListener('DOMContentLoaded', function() { 
    const loginBtn = document.getElementById('login-btn'); 
    if (loginBtn) { 
        loginBtn.addEventListener('click', function() { 
            alert('Login button clicked!'); 
        }); 
    } 
 
    const registerBtn = document.getElementById('register-btn'); 
    if (registerBtn) { 
        registerBtn.addEventListener('click', function() { 
            alert('Register button clicked!'); 
        }); 
    } 
});