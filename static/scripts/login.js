document.addEventListener('DOMContentLoaded', () => {
    const signUpButton = document.getElementById('signUp');
    const signInButton = document.getElementById('signIn');
    const container = document.getElementById('container');

    const forgotPasswordLink = document.querySelector('#forgot-password');
    const backToLoginText = document.querySelector('.reset-password-container .back-to-login');

    signUpButton.addEventListener('click', () => {
        container.classList.add("right-panel-active");
        container.classList.remove("reset-active");
    });

    signInButton.addEventListener('click', () => {
        container.classList.remove("right-panel-active");
        container.classList.remove("reset-active");
    });

    forgotPasswordLink.addEventListener('click', (e) => {
        e.preventDefault();
        container.classList.add("reset-active");
        container.classList.remove("right-panel-active");
    });

    backToLoginText.addEventListener('click', () => {
        container.classList.remove("reset-active");
    });
});
