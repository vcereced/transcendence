export async function isFriend(username1, username2) {
        
    const url = "/api/settings/isFriendShip";
    
    try {
        const response = await fetch(url, {method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username1, username2 })});    
        const data = await response.json();
            
        return data.message === "Are friends";

    } catch (error) {
        alert("Error to check are friends");
        console.error("Error:", error);
    }
}
export async function addFriend(username1, username2) {
    
    var url = "/api/settings/friendShip/";
    var action = "add";

    try {
        const response = await fetch(url + action, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username1, username2 })});
        const data = await response.json();
        
        return data.menssaje === "Are friends";
        
    } catch (error) {
        alert("Error to add friends");
        console.error("Error:", error);
    }
}

export async function removeFriend(username1, username2) {
    
    var url = "/api/settings/friendShip/";
    var action = "remove";

    try {
        const response = await fetch(url + action, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username1, username2 })});
        const data = await response.json();
            
        return data.menssaje === "Are not friends";

    } catch (error) {
        alert("Error to remove friends.");
        console.error("Error:", error);
    }
}


export async function handleButtonFriend(username1, username2) {
    var btn = document.getElementById("add-friend-btn");
    
    const friends = await isFriend(username1, username2);
    
    if (friends) {
        btn.innerHTML = "Amigo";
        btn.style.backgroundColor = "var(--primary-color)";
        btn.style.color = "white";
    } else {
        btn.innerHTML = "Añadir Amigo";
        btn.style.backgroundColor = "#f5f5f5";
        btn.style.color = "#333";
    }
}

export function goToPlayerProfile(username) {

    window.openProfilePopup(username);
}

export async function getDataUser(username) {
        
    const url = "/api/settings/dataUser";
    
    try {
        //await handleJwtToken(); // Asegura que el token JWT esté actualizado
        const response = await fetch(url, {method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username })});
        const data = await response.json();
            
        if (response.ok) {
            return data;
        } else {
            alert(data.error || "Error to obtein data from User.");}
    } catch (error) {
        alert("Error en la solicitud.");
        console.error("Error:", error);
    }
}