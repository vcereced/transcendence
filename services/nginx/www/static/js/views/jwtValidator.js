import { openWebSocket } from './websocket.js';

async function getNewAccessToken(refreshToken) {
try {
        const response = await fetch('/auth-refresh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                refresh_token: refreshToken,
            }),
        });

        if (response.ok) {
            const data = await response.json();
            return data;
        } else {
            throw new Error(`getNewAccessToken: error new access_token, response: ${response.status}`);}

    } catch (error) {
        throw new Error(`getNewAccessToken: Fetch error details: - ${error.message}`);
    }
}  

async function renovateToken() {
    const refreshToken = localStorage.getItem("refreshToken");

    if (refreshToken) {
        const data = await getNewAccessToken(refreshToken);

        if (data && data.access_token) {

            document.cookie = `accessToken=${data.access_token}; path=/; secure; SameSite=Lax`;
            console.log("Token renovated:", data);

        } else {
            throw new Error("renovateToken: cannot obtein new access token available");}
    } else {
        alert("No hay un refreshToken disponible. Redirigiendo al inicio de sesión.");
        throw new Error("renovateToken: refreshToken not available");
    }
}

async function validarToken() {
    try {
        const response = await fetch('/auth-check', {
            method: 'GET', 
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        if (response.ok) {
            return "Ok"; 
        } else if (response.status === 400) {
            console.log("validar token: Token not available");
            return "Token not available"; 
        } else if (response.status === 401) {
            console.log("validar token: Token has expired");
            return "Token has expired"; 
        } else {
            console.log("validar token: Token not valid", response.status);
            return "Token not valid"; 
        }
    } catch (error) {
        console.error("validar token: Error fetch /auth-check", error);
        return false;
    }
}

export async function handleJwtToken() {
    try{
        const response = await validarToken();
        
        if (response === "Token has expired"){
            await renovateToken();
            console.log("Token renovated, trying again conexion...");
        }

    } catch (error) {
        console.error("handleJwtToken", error);
    }

}