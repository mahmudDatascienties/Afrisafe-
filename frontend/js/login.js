/**
 * AfriSafe AI - Login Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const emailError = document.getElementById('emailError');
  const passwordError = document.getElementById('passwordError');
  const togglePasswordBtn = document.getElementById('togglePassword');
  const guestLoginBtn = document.getElementById('guestLoginBtn');
  const formAlert = document.getElementById('formAlert');

  // Clear any existing triage result on login load
  localStorage.removeItem('triageResult');

  // Toggle Password Visibility
  if (togglePasswordBtn) {
    togglePasswordBtn.addEventListener('click', () => {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      
      const eyeOpen = togglePasswordBtn.querySelector('.eye-open');
      const eyeClosed = togglePasswordBtn.querySelector('.eye-closed');
      
      if (type === 'text') {
        eyeOpen.classList.add('hidden');
        eyeClosed.classList.remove('hidden');
        togglePasswordBtn.setAttribute('aria-label', 'Hide password');
      } else {
        eyeOpen.classList.remove('hidden');
        eyeClosed.classList.add('hidden');
        togglePasswordBtn.setAttribute('aria-label', 'Show password');
      }
    });
  }

  // Handle Login Form Submission
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      
      let isValid = true;
      const email = emailInput.value.trim();
      const password = passwordInput.value;

      // Reset errors
      emailError.textContent = '';
      passwordError.textContent = '';
      emailInput.classList.remove('invalid');
      passwordInput.classList.remove('invalid');
      formAlert.classList.add('hidden');

      // Validate Email
      if (!email) {
        emailError.textContent = 'Email address is required.';
        emailInput.classList.add('invalid');
        isValid = false;
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        emailError.textContent = 'Please enter a valid email address.';
        emailInput.classList.add('invalid');
        isValid = false;
      }

      // Validate Password
      if (!password) {
        passwordError.textContent = 'Password is required.';
        passwordInput.classList.add('invalid');
        isValid = false;
      } else if (password.length < 6) {
        passwordError.textContent = 'Password must be at least 6 characters.';
        passwordInput.classList.add('invalid');
        isValid = false;
      }

      if (!isValid) return;

      // Simulate Authentication / Login Flow
      setLoadingState(true);
      
      setTimeout(() => {
        // Seamless integration. Accepts registered user profiles.
        localStorage.setItem('userSession', JSON.stringify({
          email: email,
          name: email.split('@')[0],
          type: 'User'
        }));
        
        window.location.href = 'assessment.html';
      }, 1000);
    });
  }

  // Handle Guest Login Button
  if (guestLoginBtn) {
    guestLoginBtn.addEventListener('click', () => {
      localStorage.setItem('userSession', JSON.stringify({
        email: null,
        name: 'Guest User',
        type: 'Guest'
      }));
      window.location.href = 'assessment.html';
    });
  }

  function setLoadingState(isLoading) {
    const loginBtn = document.getElementById('loginBtn');
    const btnText = loginBtn.querySelector('.btn-text');
    const btnSpinner = loginBtn.querySelector('.btn-spinner');

    if (isLoading) {
      loginBtn.disabled = true;
      btnSpinner.classList.remove('hidden');
      btnText.textContent = 'Signing In...';
    } else {
      loginBtn.disabled = false;
      btnSpinner.classList.add('hidden');
      btnText.textContent = 'Sign In';
    }
  }
});
