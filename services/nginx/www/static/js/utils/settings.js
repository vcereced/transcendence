
export async function showUsername(email){
    
    //await handleJwtToken();
    await fetch('/api/settings/dataUser', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
    })
    .then(response => response.json())
    .then(data => { document.getElementById('current-username').textContent = data.username;})
    .catch(error => {
        alert(data.error || "Error to obtein the username.");
        console.error("Error to obtein the username:", error);
    });
}

export async function updateUsername(email, newUsername) {
    const url = "/api/settings/updateName";
    
    try {
        //await handleJwtToken();
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, newUsername })
        });

        const data = await response.json();
        if (response.ok) {
            window.closeSettingsPopup();
        } else {
            alert(data.error || "Error al actualizar el nombre de usuario");
        }
    } catch (error) {
        alert("Error en la solicitud");
        console.error("Error:", error);
    }
}

export async function updatePassword(email, oldPass, newPass1, newPass2) {
    
    if(!oldPass || !newPass1 || !newPass2) {
        alert("todos los campos son necesarios");
        return;
    }
    
    if (newPass1 !== newPass2) {
        alert("Las nuevas contraseñas no coinciden.");
        return;
    }

    const url = "/api/settings/updatePassword";
    
    try {
        //await handleJwtToken(); // Asegura que el token JWT esté actualizado

        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email,
                oldPassword: oldPass,
                newPassword: newPass1
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            window.closeSettingsPopup();
        } else {
            alert(data.error || "Error al cambiar la contraseña.");
        }
    } catch (error) {
        alert("Error en la solicitud.");
        console.error("Error:", error);
    }
}

export async function showPicture(email) {

    const url = "/api/settings/dataUser";
    
    try {

        //await handleJwtToken(); // Asegura que el token JWT esté actualizado
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();
        
        if (response.ok) {
            document.getElementById("current-profile-pic").src = data.picture_url;
        } else {
            alert(data.error || "Error to change the picture profile.");
        }
    } catch (error) {
        alert("Error to fetch to change picture.");
        console.error("Error:", error);
    }
}

export async function updatePicture(email, src) {

    const url = "/api/settings/updatePictureUrl";

    try {
        //await handleJwtToken(); // Asegura que el token JWT esté actualizado

        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, src })
        });

        const data = await response.json();
        
        if (response.ok) {
            return;
        } else {
            alert(data.error || "Error to change the picture profile.");
        }
    } catch (error) {
        alert("Error to change the picture profile.");
        console.error("Error:", error);
    }

}
