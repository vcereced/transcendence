export async function getNewAccessToken(urlRefresh, refreshToken) {
    try {
        const response = await fetch(urlRefresh, {
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
            console.log("New token recieved:");
            return data; // Devuelve los datos, que deben incluir el nuevo access_token
        } else {
            console.error(`Error getting new access_token: ${response.status}`);
        }
        return null;
    } catch (error) {
        console.error("getNewAccessToken: error fetch /auth-refresh", error);
    }
}  

export async function renovateToken(urlRefresh, refreshToken) {

    if (refreshToken) {
        const data = await getNewAccessToken(urlRefresh, refreshToken); 
        
        if (data && data.access_token) {
            document.cookie = `accessToken=${data.accessToken}; path=/; secure; SameSite=Lax`;
            //guardarAccessToken(data.access_token); // Guarda el nuevo token
            return;
            //return data.access_token; // Retorna el nuevo access token
        } else {
            console.error("renovateToken: error new token");
            return null;
        }
    } else {
        console.error("renovarToken: No hay refresh_token disponible");
        alert("No hay un refreshToken disponible. Vuelve a iniciar sesión.");
    }
}

async function validateToken(urlCheck) {
    try {
        const response = await fetch(urlCheck, {
            method: 'GET', 
        });

        if (response.ok) {
            console.log("token OK");
            return "Ok"; 
        } else if (response.status === 400) {
            console.log("validar token: Token not available");
            return "Token not available"; 
        } else if (response.status === 401 && response.error === 'Token has expired') {
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

export async function jwtValidator() {
    let urlCheck = '/auth-check';
    let urlRefresh = '/auth-refresh';
    let refreshToken = localStorage.getItem("refreshToken");

    const result = await validateToken(urlCheck);

    if (result === "Ok") {
        console.log("first OK go to openwebsoket");
        abrirWebSocket(roomName); ///HARCODED T¿FOR WEBSOCKETS
        //return true;
    } else if (result === "Token has expired") {
        token = await renovateToken(urlRefresh, refreshToken); // Si el token expiró, intenta renovarlo
        console.log("token renovated go to validartoken");
        const renewedResult = await validarToken(urlCheck); // Validar el nuevo token

        if (renewedResult === "Ok") {
            console.log("token validated go to openwebsoket");
            abrirWebSocket(roomName); ///HARCODED T¿FOR WEBSOCKETS
            //return true;
        } else {
            console.error("Cannot validate new token");
            return false
        }
    } else {
        console.error("Token invalid or who knows madafaka, error:", result);
        return false;
    }
}