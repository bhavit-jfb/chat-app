document.getElementById("message-form").addEventListener("submit", function(e){
    e.preventDefault();

    const formData = new FormData(this);

    fetch("/send-message", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        console.log(data);
    });
});