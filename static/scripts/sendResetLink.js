const form = document.getElementById('reset-form');
  const responseMessage = document.getElementById('response-message');

  function showMessage(text, isSuccess) {
    responseMessage.textContent = text;
    responseMessage.style.color = 'gray';
    responseMessage.style.fontSize = '0.9rem';
    responseMessage.style.visibility = 'visible';
  }

  function hideMessage() {
    responseMessage.style.visibility = 'hidden';
    responseMessage.textContent = '';
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    hideMessage();

    const formData = new FormData(form);
    const data = new URLSearchParams(formData);

    try {
      const response = await fetch('/api/sendResetToken', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: data.toString()
      });

      const result = await response.json();
      console.log("API response JSON:", result);

      // Show message from API response
      showMessage(result.message || 'No message returned', result.success);
    } catch (error) {
      showMessage('An error occurred while sending request.', false);
    }
  });