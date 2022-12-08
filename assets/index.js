document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
        
        const toggle = document.getElementById("dark-mode-switch");
        const profile_img = document.getElementById("profile_img");

        toggle.onclick = event => {
            event.preventDefault();
            document.body.classList.toggle("dark");
            profile_img.classList.toggle("dark-img");
        }
    }, 500);
});

