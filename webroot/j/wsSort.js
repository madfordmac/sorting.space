window.addEventListener("DOMContentLoaded", () => {
    // Open web socket
    const websocket = new WebSocket("ws://localhost:9832/");

    // Debug action auto-submits a list
    /* websocket.onopen = () => websocket.send(JSON.stringify({
        "type": "hello",
        "data": [
            "McDonald's",
            "Wendy's",
            "Burger King",
            "Culvers",
            "Taco Bell",
            "Dairy Queen"
        ]
    })); */

    // Respond to incoming messages
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

    // Function to add a new item to the input list
    const addItem = () => {
        const new_li = document.createElement("li");
        const new_input = document.createElement("input");
        new_input.type = "text";
        new_li.appendChild(new_input);
        document.getElementById("input_list").appendChild(new_li);
    };

    // Add action to the "+" button
    document.getElementById("plus").onclick = addItem;

    // Function to submit the list of items
    const submitList = () => {
        const data = [];
        const node_list = document.querySelectorAll('ol#input_list li');
        node_list.forEach((li) => {
            data.push(li.firstElementChild.value);
        });
        websocket.send(JSON.stringify({
            "type": "hello",
            "data": data
        }));
        document.getElementById("build").style.display = "none";
        document.getElementById("rank").style.display = "block";
    };

    // Add action to the "Submit" button
    document.getElementById("sortbtn").onclick = submitList;

    // Add action to the "Choose A" button
    document.getElementById("a").onclick = () => {
        websocket.send(JSON.stringify({
            "type": "answer",
            "answer": "a"
        }));
    };

    // Add action to the "Choose B" button
    document.getElementById("b").onclick = () => {
        websocket.send(JSON.stringify({
            "type": "answer",
            "answer": "b"
        }));
    };
})