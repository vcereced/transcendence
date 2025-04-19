import { handleJwtToken } from '../views/jwtValidator.js';

export async function showUsername(email){
    
    await handleJwtToken();
    await fetch('/api/settings/dataUser', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
    })
    .then(response => response.json())
    .then(data => {document.getElementById('current-username').textContent = data.username;})
    .catch(error => {
        window.showPopup("Error al obtener el nombre de usuario");
    });
}

export async function updateUsername(email, newUsername) {
    const url = "/api/settings/updateName";
    
    try {
        await handleJwtToken();
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, newUsername })
        });

        const data = await response.json();
        if (response.ok) {
            window.sessionStorage.setItem("username", newUsername);
            window.showPopup("Nombre de usuario actualizado correctamente");
            window.closeSettingsPopup();
        } else {
            window.showPopup("Error al actualizar el nombre de usuario");
        }
    } catch (error) {
        window.showPopup("Error al actualizar el nombre de usuario");
    }
}

export async function updatePassword(email, oldPass, newPass1, newPass2) {
    
    if(!oldPass || !newPass1 || !newPass2) {
        window.showPopup("Todos los campos son necesarios");
        return;
    }
    
    if (newPass1 !== newPass2) {
        window.showPopup("Las nueva contraseña no coincide con la confirmación");
        return;
    }

    const url = "/api/settings/updatePassword";
    
    try {
        await handleJwtToken(); // Asegura que el token JWT esté actualizado

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
            window.showPopup("Contraseña cambiada correctamente");
            window.closeSettingsPopup();
        } else {
            window.showPopup("Error al cambiar la contraseña");
        }
    } catch (error) {
        window.showPopup("Error al cambiar la contraseña");
    }
}

export async function showPicture(email) {

    const url = "/api/settings/dataUser";
    
    try {

        await handleJwtToken(); // Asegura que el token JWT esté actualizado
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
            window.showPopup("Error al obtener la imagen de perfil");
        }
    } catch (error) {
        window.showPopup("Error al obtener la imagen de perfil");
    }
}

export async function updatePicture(email, src) {

    const url = "/api/settings/updatePictureUrl";

    try {
        await handleJwtToken(); // Asegura que el token JWT esté actualizado

        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, src })
        });

        const data = await response.json();
        
        if (response.ok) {
            window.showPopup("Imagen de perfil actualizada correctamente");
            return;
        } else {
            window.showPopup(data.error);
        }
    } catch (error) {
        window.showPopup("Error al actualizar la imagen de perfil");
    }

}

export async function uploadImage(formData) {

    const url = "/api/settings/upload-profile-pic";

    try {
        await handleJwtToken(); // Asegura que el token JWT esté actualizado

        const response = await fetch(url, {
            method: "POST",
            body: formData,
        });

        const data = await response.json();
        
        if (response.ok) {
            window.showPopup("Imagen de perfil actualizada correctamente");
            return;
        } else {
            window.showPopup(data.error);
        }
    } catch (error) {
        window.showPopup(error);
    }

}