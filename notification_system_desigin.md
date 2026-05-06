# Notification System Design

The task is to create a notification app that alerts the user when they have logged in.

## Overview

The system consists of three main components:
- Frontend: React-based user interface for login and displaying notifications.
- Middleware: Acts as a proxy to prevent DoS attacks and rate limit requests.
- Backend: FastAPI server that handles authentication and notification logic.

## Frontend

- Built with React.
- Features a login form where users enter credentials.
- Upon successful login, displays an alert notification to the user.
- Communicates with the middleware for login requests.

## Backend

- Managed by uv, using FastAPI framework.
- Provides REST API endpoints for authentication.
- Validates user credentials.
- Upon successful login, triggers the notification to the frontend.

## Middleware

- Implemented to prevent DoS attacks from clients.
- Uses rate limiting to control the number of requests per user/IP.
- fastapi
## API Design

### Login Endpoint
- 
### Notification Flow
1. User submits login form on frontend.
2. Frontend sends POST /login to middleware.
3. Middleware checks rate limits, forwards to backend if allowed.
4. Backend validates credentials.
5. If valid, backend responds with success.
6. Frontend displays alert: "You have logged in."

## sequirty 
- the passwords are hashed

## stage 1 
    - creating a simple we page for users to login

## stage 2 
    - adding notifications in sqlite.db whcih is lightweight structure 

## stage 3 
    - we should not make database t overladed 
    - for that we keep a data based for each day or week, currently i am choosing weekly based model, 
    - based on the date time we can query dataa base

## stage 4
    - due to somenetworktrubble or soething else the usersare getting overwlemed 
    - to fix this before updating we will check upding
    - for every fimutes if hereoaded 10 times, he visited at this 
    - this distrctly reduce the data stroage 
    - also keep we shuld not merge thinsalready we have mergerd 

## stage 5
    - in the stage 5 case we need to notify all the people in resective field 
    - we should menize the database as well
    - in this we need to implemnt database, based on types on user,
    - for every 5 minutes the app will check weather he recivied notifictio n or not
    - for this also we need new databbase 

## stage 6 impleting the priotrity,
- if we want include pritrity we need to llm,assign the score, whcih too much for this demo, 
- in this case we will add results based on the person who is 0creting notfications , bye 
- wait still another stage 

## stage 7 
- now we need to implemnet everything and make it better, that's it 