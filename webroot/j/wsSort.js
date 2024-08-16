window.addEventListener("DOMContentLoaded", () => {
    // Open web socket
    const websocket = new WebSocket(`ws://${window.location.hostname}:9832/`);

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
                document.getElementById("rank").classList.add("d-none");
                document.getElementById("result").classList.remove("d-none");
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

    const getJSON = (url, callback) => {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.responseType = 'json';
        xhr.onload = () => {
            const status = xhr.status;
            if (status === 200) {
                callback(null, xhr.response);
            }
            else {
                callback(status, xhr.response);
            }
        };
        xhr.send();
    };

    const args = new URLSearchParams(window.location.search);
    const list = args.get("list");
    if (list) {
        getJSON(`/lists/${list}.json`, (err, data) => {
            if (err !== null) {
                console.log(`Error ${err} getting lists: ${data}`);
            }
            else {
                let first = true;
                data.forEach((value, index, array) => {
                    if (first) {
                        document.getElementById("input_list").querySelector("input").value = value;
                        first = false;
                    }
                    else {
                        addItem(value);
                    };
                });
            }
        })
    }

    /*┏━━━━━━━━━━━━━━━━━┓
      ┃                 ┃
      ┃  Tab Functions  ┃
      ┃                 ┃
      ┗━━━━━━━━━━━━━━━━━┛*/
    const tab_list = [
        "sort-tab",
        "about-tab"
    ];

    const setActiveTab = (active) => {
        for (const tab of tab_list) {
            const tab_div = document.getElementById(tab + "-div");
            const tab_li = document.getElementById(tab + "-li")
            if (tab == active) {
                tab_div.classList.remove("d-none");
                tab_li.classList.add("active");
            }
            else {
                tab_div.classList.add("d-none")
                tab_li.classList.remove("active");
            }
        }
    };

    for (const tab of tab_list) {
        document.getElementById(tab + "-a").onclick = () => {
            setActiveTab(tab);
        }
    };

    // Function to add a new item to the input list
    let nx_id = 2;
    const addItem = (text) => {
        const item_id = `option-${nx_id}`;
        const new_li = document.createElement("li");
        new_li.id = item_id;
        const new_input = document.createElement("input");
        new_input.type = "text";
        if (text) {
            new_input.value = text;
        }
        new_li.appendChild(new_input);
        const new_dbtn = document.createElement("button");
        new_dbtn.classList.add("btn", "btn-error");
        new_dbtn.onclick = () => {
            delItem(item_id);
        }
        const delete_icon = document.createElement("i");
        delete_icon.classList.add("icon", "icon-delete");
        new_dbtn.appendChild(delete_icon);
        new_li.appendChild(new_dbtn);
        nx_id += 1;
        document.getElementById("input_list").appendChild(new_li);
    };

    // Function to delete an item from the input list
    const delItem = (item) => {
        document.getElementById(item).remove();
    };
    document.getElementById("option-1").querySelector("button").onclick = () => {
        delItem("option-1");
    };

    // Add action to the "+" button
    document.getElementById("plus").onclick = () => {
        addItem("");
    };

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
        document.getElementById("build").classList.add("d-none");
        document.getElementById("rank").classList.remove("d-none");
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
