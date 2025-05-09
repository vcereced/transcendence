<p align="center">
  <a>
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/42_Logo.svg/1200px-42_Logo.svg.png" alt="Logo" width="200" height="200">
  </a>

  <p align="center">
     Full-stack web application<br>
    on microservices.
    <br />
	</p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Makefile-8A2BE2">
  <img src="https://img.shields.io/badge/C-4682B4">
  <img src="https://img.shields.io/badge/Shell-2E8B57">
  <img src="https://img.shields.io/badge/Gcc-00FF00">
  
</p>

## &#x2728; What is transcendence?
Diseñar, organizar y desarrollar u  proyecto full-stack en un equipo de desarrollo de 3 personas. Se trata de competitive multiplayer version of Pong.
- Victor Cereceda [Github](https://github.com/vcereced)
- David Garizado Toro [Github](https://github.com/garydd1)
- Fernando Gómez - [Github](https://github.com/fer5899)
  

https://github.com/user-attachments/assets/b8a86d5c-5efd-4703-9082-53c508d4c178



## Requirements
- Frontend vanilla JS.
- Backend Django Framework with PostgreSQL.
- Prohibido usar librerías que resuelvan funciones completas.
- La web debe ser una SPA, sin errores visibles y compatible con Google Chrome actualizado.
- Todo debe correr con un solo comando usando Docker.

## User Management
- Registro, login seguros y manejo de duplicados 
- Edición de perfil y subida de avatar (con opción por defecto).
- Sistema de amigos con estado en línea.
- Perfil con estadísticas (victorias/derrotas) y historial de partidas 1v1.

## Cybersecurity
- Contraseñas hasheadas.
- Protección contra SQLi/XSS.
- HTTPS obligatorio y wss en Websockets.
- 2FA a traves de e-mail.
- JWT para gestionar autenticación y autorización de forma segura.
- Nada de credenciales en el repo, usá .env.

## Gameplay and user managementy
- Remote players: 2 jugadores jueguen desde distintos dispositivos vía red. Manejar lag y desconexiones.
- Minijuego + historial + matchmaking:

## AI-Algo
- Prohibido el uso de A* algorithm
- Simular el comportamiento humano siendo capaz de ganar partidas.

## Devops
- Backend en microservicios modulares, mantenibles y escalables.
- Comunicacion usando REST APIs mediantes brokers.

## &#x1F6E0; Diagrama

Schema of global logic:
https://drive.google.com/file/d/1Llc0r4MQEMciNO2diklEgxHzNlYJo6Po/view?usp=sharing

## &#x1F4BB; Usage

First of all create a .env archivo con lo siguiente:
```
#Enviroment Variables NEEDED for the project


    #Django settings
DJANGO_SECRET_KEY=xxx
POSTGRES_PASSWORD=xxx
POSTGRES_USER=xxx


    #Email settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=xxx
EMAIL_HOST_PASSWORD=xxx

    #Blockchain settings
BLOCKCHAIN_API_URL=xxx
CONTRACT_ADDRESS=xxx

SEPOLIA_PRIVATE_KEY=xxx
```

`make` to build and start containers.

`make stop` to stop all containers.

`make fclean` to stop, delete containers and remove volumens.

`make re` to fclean and make again.

## &#x1F4D6; Examples

Execute this command in the terminal to deploy the web-app.

```bash
make
```

Let's try in the browser:

`https://localhost:8443`


