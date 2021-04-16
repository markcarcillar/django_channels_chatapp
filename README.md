#  Chat App
- A simple chat application that is created using Django with Channels.

## Features
1. Authentication
   - Login
   - Logout
   - Register
2. User per user chat. All user can chat each other. The chat is secured because it has a key that is used for group name on consumer to only the sender and receiver can receive the chat through websocket.
   - **Key count per user**
   - User Count | Key Count
   - 1          | 0
   - 2          | 1
   - 3          | 3
   - 4          | 4