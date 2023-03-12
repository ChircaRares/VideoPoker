const api_url = "http://localhost:5000/"

function set_divs(new_game_div, change_cards_div, msg_div){
    document.getElementById("newGame").style.display = new_game_div
    document.getElementById("changeCards").style.display = change_cards_div
    document.getElementById("msg").innerHTML = msg_div
}

function turn_card(cardId, data, backgroundColor, color){
    document.getElementById(cardId).innerHTML = data;
    document.getElementById(cardId).style.backgroundColor = backgroundColor;
    document.getElementById(cardId).style.color = color;
}

async function get_points(mode){
    const resp = await fetch(api_url + "points?mode=" + mode);
    let points = await resp.json();
    document.getElementById("points").innerHTML = points.toString()
}

async function deal_cards() {
    const response = await fetch(api_url + "cards?number=5&deal=first_deal")
    let cards = await response.json()
    for(let i = 0; i < 5; i++) {
        turn_card("card" + i, cards[i], "white", "black")
    }
    set_divs("none", "block", "")
    await get_points("new_deal")
}

async function change_old_cards() {
    let changed_cards = []
    const btns = document.querySelectorAll('.button-fancy')
    btns.forEach(function(btn){
        if(btn.style.backgroundColor === "blue")
            changed_cards += btn.id[4]
    })
    let final_cards = {}
    if(changed_cards.length) {
        for (let i = 0; i < changed_cards.length; i++) {
            const response = await fetch(api_url + "cards?number=1&deal=another_deal&pos=" + changed_cards[i]);
            let data = await response.json();
            if (i === changed_cards.length - 1) {
                final_cards = data;
            }
            document.getElementById("card" + changed_cards[i]).innerHTML = data[changed_cards[i]];
            document.getElementById("card" + changed_cards[i]).style.backgroundColor = "white";
            document.getElementById("card" + changed_cards[i]).style.color = "black";
        }
    }else{
        const response = await fetch(api_url + "cards?number=1&pos=0");
        final_cards = await response.json();
    }

    const resp = await fetch(api_url + "win?finalCards=" + final_cards);
    let msg = await resp.text()
    set_divs("block", "none", msg.toString())
    await get_points("update_points")
}
