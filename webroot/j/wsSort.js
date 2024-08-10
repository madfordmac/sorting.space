window.addEventListener("DOMContentLoaded", () => {
    const websocket = new WebSocket("ws://localhost:9832/");
    websocket.onopen = () => websocket.send(JSON.stringify({
        "type": "hello",
        "data": [
            "McDonald's",
            "Wendy's",
            "Burger King",
            "Culvers",
            "Taco Bell",
            "Dairy Queen"
        ]
    }));

    websocket.onmessage = ({data}) => {
        const mesg = JSON.parse(data);
        switch(mesg.type) {
            case "error":
                const err = document.createElement("p");
                const errTxt = document.createTextNode(mesg.message);
                err.appendChild(errTxt);
                document.body.appendChild(err);
                break;
            case "compare":
                document.getElementById("a").textContent = mesg.a;
                document.getElementById("b").textContent = mesg.b;
                break;
            case "result":
                document.getElementById("rank").style.display = "none";
                document.getElementById("result").style.display = "block";
                const result_list = document.getElementById("result_list");
                for (const item_text of mesg.data) {
                    const list_item = document.createElement("li");
                    list_item.textContent = item_text;
                    result_list.appendChild(list_item);
                };
                break;
            default:
                console.error("unsupported event type", mesg);
        };
    };

    document.getElementById("a").onclick = () => {
        websocket.send(JSON.stringify({
            "type": "answer",
            "answer": "a"
        }));
    };

    document.getElementById("b").onclick = () => {
        websocket.send(JSON.stringify({
            "type": "answer",
            "answer": "b"
        }));
    };
})