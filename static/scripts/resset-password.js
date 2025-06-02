  const form = document.getElementById('reset-form');
  const successMessage = document.getElementById('success-message');
  const errorMessage = document.getElementById('error-message');
  const backToLogin = document.getElementById('back-to-login');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    // Clear previous error
    errorMessage.textContent = '';
    errorMessage.style.color = '';
    errorMessage.style.visibility = 'visible';

    const password = form.password.value.trim();
    const confirmPassword = form.confirmPassword.value.trim();

    // Validation
    if (!password) {
      errorMessage.textContent = 'Password is required.';
      errorMessage.style.color = 'red';
      return;
    }
    if (password !== confirmPassword) {
      errorMessage.textContent = 'Passwords do not match.';
      errorMessage.style.color = 'red';
      return;
    }

    // Prepare form data
    const formData = new FormData(form);
    const data = new URLSearchParams(formData);

    try {
      const response = await fetch('/api/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: data.toString()
      });

      const result = await response.json();

      if (result.success) {
        // On success, hide form and show success message
        form.style.display = 'none';
        successMessage.textContent = result.message || 'Password has been reset successfully.';
        successMessage.style.display = 'block';
        backToLogin.style.display = 'block';
        
      } else {
        // Show API error message
        errorMessage.textContent = result.message || 'Something went wrong.';
        errorMessage.style.color = 'red';
      }
    } catch (error) {
      errorMessage.textContent = 'An error occurred while sending request.';
      errorMessage.style.color = 'red';
      console.error('Fetch error:', error);
    }
  });