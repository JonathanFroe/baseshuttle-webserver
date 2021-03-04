var socket = io();
var all_player = null;
var turn = null;
var card_text = null;

socket.on("redirect", function (data) {
    window.location = data;
});

socket.on("alert", function (msg) {
    var alert = document.createElement("div");
    alert.className = "alert";
    alert.innerHTML = msg;
    setTimeout(function () {
        alert.parentNode.removeChild(alert);
    }, 2000);
    document.body.appendChild(alert);
});

socket.on("update", function () {
    console.log("update");
    socket.emit("get_player");
    socket.emit("get_cards");
    socket.emit("get_turn");
});

socket.on("turn", function (msg) {
    turn = msg;
    if (card_text == null) {
        for (player of all_player) {
            if (player[0] == turn) {
                if (player[0] == document.getElementById("my_id").value) {
                    document.getElementById("info_text").innerHTML =
                        "Du bist dran! Wähle eine Karte";
                    document
                        .getElementById("info_text")
                        .classList.add("selected");
                } else {
                    document.getElementById("info_text").innerHTML =
                        player[1] + " ist gerade an der Reihe";
                    document
                        .getElementById("info_text")
                        .classList.remove("selected");
                }
            }
        }
    }
});

socket.on("chose_player", function (msg) {
    all_player = msg;
    var old_buttons = document.getElementsByClassName("player");
    while (old_buttons[0]) {
        old_buttons[0].parentNode.removeChild(old_buttons[0]);
    }
    for (player of msg) {
        if (player[0] != document.getElementById("my_id").value) {
            var button = document.createElement("button");
            button.id = player[0];
            button.className = "player";
            button.innerHTML = player[1];
            button.setAttribute("onclick", "select_player(this.id)");
            document.getElementById("player_container").appendChild(button);
        }
    }
});

socket.on("chose_card", function (msg) {
    var old_buttons = document.getElementsByClassName("card");
    while (old_buttons[0]) {
        old_buttons[0].parentNode.removeChild(old_buttons[0]);
    }
    if (parseInt(msg) > 0) {
        for (var card = 0; card < parseInt(msg); card++) {
            var button = document.createElement("button");
            button.id = card;
            button.className = "card";
            button.innerHTML = "Karte";
            button.setAttribute("onclick", "select_card(this.id)");
            document.getElementById("card_container").appendChild(button);
        }
    } else {
        socket.emit("get_data");
    }
});

socket.on("card_text", function (msg) {
    if (msg[0] == document.getElementById("my_id").value) {
        card_text = msg[1];
        document.getElementById("info_text").innerHTML =
            'Deine Karte lautet: "' + card_text + '". Wähle einen Spieler!';
    }
});

socket.on("data", function (msg) {
    if (msg[0] == document.getElementById("my_id").value) {
        var old_buttons = document.getElementsByClassName("card");
        while (old_buttons[0]) {
            old_buttons[0].parentNode.removeChild(old_buttons[0]);
        }
        var old_buttons = document.getElementsByClassName("player");
        while (old_buttons[0]) {
            old_buttons[0].parentNode.removeChild(old_buttons[0]);
        }
        var old_div = document.getElementsByClassName("data");
        while (old_div[0]) {
            old_div[0].parentNode.removeChild(old_div[0]);
        }
        if (msg[1] == null) {
            msg[1] = ["Leider wurde dir nichts geschickt!"];
        }
        for (element of msg[1]) {
            var div = document.createElement("div");
            div.className = "data";
            div.innerHTML = element;
            document.getElementById("data_container").appendChild(div);
        }
        card_text =
            "Die Runde ist vorbei. Hier sind deine zugeschickten Karten:";
        document.getElementById("info_text").innerHTML = card_text;
    }
});

function select_player(id) {
    if (card_text != null) {
        socket.emit("select_player", [id, card_text]);
        card_text = null;
        document.getElementById("info_text").innerHTML = null;
    }
}

function select_card(id) {
    if (turn == document.getElementById("my_id").value) {
        if (card_text == null) {
            socket.emit("select_card", id);
        }
    }
}
