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
Design, organize, and develop a full-stack project as a team of 3 developers. It’s a competitive multiplayer version of Pong.
- Victor Cereceda [Github](https://github.com/vcereced)
- David Garizado Toro [Github](https://github.com/garydd1)
- Fernando Gómez - [Github](https://github.com/fer5899)

https://github.com/user-attachments/assets/1e830472-92b7-48c1-8d8a-aa5731472875

## Requirements
- Frontend in vanilla JS
- Backend using Django with PostgreSQL
- No libraries that solve entire features allowed
- Must be a single-page application (SPA)
- Must run smoothly on up-to-date Google Chrome
- Entire project should launch with a single Docker command

## User Management
- Secure registration, login, and duplicate handling
- Profile editing and avatar upload (with default option)
- Friend system with online status
- Profile page showing stats (wins/losses) and match history (1v1)

## Cybersecurity
- Passwords hashed
- Protection against SQL injection and XSS
- HTTPS required, and wss:// for WebSocket connections
- Two-factor authentication via email
- JWT for secure authentication and authorization
- No credentials in the repository – use .env files

## Gameplay and user managementy
- Remote gameplay between 2 players from different devices
- Handle lag and disconnections
- Includes a minigame, history tracking, and matchmaking

## AI-Algo
- A* algorithm is forbidden
- Simulate human-like behavior capable of winning games

## Devops
- Backend divided into modular, maintainable, and scalable microservices
- REST API communication via message brokers

## &#x1F6E0; Diagrama

   Project architecture schema:

	https://drive.google.com/file/d/1Llc0r4MQEMciNO2diklEgxHzNlYJo6Po/view?usp=sharing

## &#x1F4BB; Usage

First, create a .env file with the following:
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

`make fclean` to remove containers and volumes.

`make re` to rebuild everything.

## &#x1F4D6; Examples

Execute this command in the terminal to deploy the web-app.


	make


Open in browser:

	https://localhost:8443


