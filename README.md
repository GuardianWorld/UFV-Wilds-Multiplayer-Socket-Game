# UFV Wilds — Multiplayer Socket Game

A real-time multiplayer card game inspired by Super Trunfo, built in Python using socket-based networking, multithreaded server architecture, and a custom JSON communication protocol.

Developed as part of CCF 355 — Distributed Systems (UFV).

---

# Overview

UFV Wilds is a 3-player online card game where players compete to capture all opponent cards through attribute-based battles.

The system is composed of a central authoritative server and multiple Pygame-based clients, communicating through raw TCP sockets and structured JSON messages.

The project explores:

- Distributed systems design
- Real-time multiplayer synchronization
- Thread-safe server architecture
- Authentication and session control
- Database-backed game state persistence

---

# Game Concept

- 3 players per match
- Each player starts with a deck of cards
- Cards contain multiple attributes (Super Trunfo-style comparison system)
- Players select attributes and compete in rounds
- Winner of each round collects cards
- Game ends when a player captures all cards or reaches victory condition

---

# Architecture

## System Design

```
Clients (Pygame UI)
        │
        │ JSON over TCP sockets
        ▼
Authoritative Game Server
        │
 ┌───────┼──────────────────────┐
 │       │                      │
Matchmaking Thread   Client Handler Threads   Admin Terminal Thread
 │
 ▼
PlayField (Active Match Instance)
```

## Server Architecture

The server is multithreaded and composed of three core components:

### 1. Main Thread
- Accepts incoming connections
- Spawns dedicated client handler threads
- Manages lifecycle of connections

### 2. Terminal Thread (Admin Control)

Provides runtime administration:

- shutdown — graceful server shutdown
- status — active connections, players, matches
- statistics — system metrics
- config — runtime configuration management
- kick / ban — player moderation
- delete user — database management

### 3. Matchmaking Thread
- Monitors queue of players searching for matches
- Groups players in sets of 3
- Spawns isolated match instances (PlayField threads)

## Networking Model

### Communication Protocol

All client-server communication uses JSON messages:

```
{
  "Token": "auth_token",
  "Message": "login/register/game_action",
  "Command": "optional_action",
  "Payload": {}
}
```

### Key Features
- Keep-alive socket mechanism
- Timeout-based connection validation
- Thread-per-client architecture
- JSON-based command routing system

### Authentication & Security

The system includes lightweight security mechanisms:

- Password hashing using SHA-256
- JWT-based authentication tokens
- Token validation on all gameplay actions
- Session tracking via active user registry
- Admin-only terminal commands

## Database Design

SQLite is used for persistence.

Core Tables:

- Users — authentication and user profiles
- Cards — card definitions and attributes
- UserCards — ownership mapping (up to 3 copies per card)
- Decks — user deck configurations
- DeckCards — deck composition (max 9 cards per deck)
- SystemConfig — server configuration
- Statistics — match and system analytics

---

## Match Flow
1. 3 authenticated players are grouped
2. Decks are loaded and shuffled
3. Turn order is randomized
4. Each player receives 3 cards
5. Gameplay loop begins:
- Active player selects attribute
- All players play a card
- Server determines winner
- Winner collects cards
- Hands are replenished
6. Match ends when a player runs out of cards or wins condition is met
7. Players return to lobby

---

## Client Architecture

The client is split into two layers:

1. Network Layer
- Manages socket communication
- Handles JSON encoding/decoding
- Maintains connection state
- Processes server commands
2. UI Layer (Pygame)
- Login / registration screens
- Lobby and matchmaking UI
- Match interface
- Deck management system
- Reward and results screens

## Inter-Thread Communication

The client uses thread-safe queues to separate concerns:

- UI thread → sends user actions to network layer
- Network thread → forwards server responses to UI

This prevents blocking and ensures smooth rendering during network operations.

## Asset Synchronization

Upon login:

- Server sends file list with checksums
- Client verifies local assets
- Missing or corrupted files are requested
- Files are transmitted in base64-encoded JSON chunks (~4096 bytes)

---

## Technologies
- Python 3
- socket
- threading
- JSON
- SQLite
- hashlib (SHA-256)
- PyJWT
- Pygame

---

## Limitations
- No encryption beyond authentication tokens
- Limited scalability (3-player match design)
- Basic matchmaking logic
- No dedicated anti-cheat system
- Prototype-level networking protocol

---

# Highlights
- Full custom multiplayer backend (no engine/framework)
- Threaded server architecture
- JWT authentication system
- SQLite-backed persistence layer
- Real-time gameplay synchronization
- Admin terminal system for server control
- Custom JSON protocol over TCP sockets

--- 
Related Work
- CCF 355 — UFV Distributed Systems Project
