
//     function getRemedy() {
//         let query = document.getElementById("query").value;
//         let language = document.getElementById("language").value;

//         fetch("/remedy", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ query: query, lang: language })
//         })
//         .then(response => response.json())
//         .then(data => {
//             document.getElementById("response").innerText = data.response;
//         })
//         .catch(error => console.error("Error:", error));
//     }



