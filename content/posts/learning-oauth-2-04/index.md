---
title: "Using the Access Token on a Protected API"
date: 2026-06-10
categories: 
  - "coding"
  - "software"
tags: 
  - "oauth2"
---

## Why v03 was not the finish line

[v03]({{< relref "posts/learning-oauth-2-03" >}}) closed the authorization half of OAuth: `state` for CSRF, PKCE for code interception, and `POST /token` to mint an `access_token`. After a successful login, the callback page displayed that token as a string.

That is a useful checkpoint. It is not a complete application experience. The token is supposed to be a credential. Something has to accept it and return data only the authenticated user should see.

That something is the resource server. In [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749#section-1.1), OAuth names four roles:

| Role | This lab |
|------|----------|
| Resource owner | You, logging in as `user0` |
| Client | Flask app on `:25001` |
| Authorization server | Flask app on `:25000` (`/authorize`, `/token`) |
| Resource server | Same Flask app on `:25000` (`GET /api/me`) |

v04 adds the last row in practice: a protected endpoint and client wiring that uses the token end to end.

### Example: token with nowhere to go

**Setup:** v03 ends with `access_token` on the callback page. Imagine the client treats "I have a token string" as logged in, but never calls an API.

**What is missing:**

1. User completes login and sees a random token in the browser.
2. They refresh the page; unless you stored the token, it is gone.
3. Even if you copy it somewhere, the app never proves the token works; it never loads `user0`'s profile.
4. A stolen token sitting in browser history is useless to the app.

**What v04 fixes:** The client stores the token in session, calls a protected API with `Authorization: Bearer …`, and shows a profile page. The auth server validates the token before returning user JSON. Login now means: "this token identifies me, and the API agrees."

## How v04 uses the token

Bearer token usage is defined in [RFC 6750](https://datatracker.ietf.org/doc/html/rfc6750). The client sends the token in an HTTP header; the resource server validates it and returns (or denies) the resource. There are no new OAuth query parameters. This is HTTP semantics on top of what v03 already minted.

### Resource server: GET /api/me

There is a new file: `server/routes/resource.py` that implements the following:

1. Reads `Authorization: Bearer <access_token>`.
2. Looks up the token in `memory.access_tokens` (same dict `POST /token` writes to).
3. Returns 401 if the header is missing, malformed, unknown, or past `expires_at`.
4. Resolves `user_id` from the token record to a row in `memory.users`.
5. Returns JSON, e.g. `{"user_id": "user0", "username": "User Number 0", "email": "user0@oauth-lab.me"}`.

You can test it without the client:

```bash
curl -s http://localhost:25000/api/me \
  -H "Authorization: Bearer PASTE_ACCESS_TOKEN_HERE"
```

### Client: store, fetch, display

Three changes on top of v03:

**1. Callback (`/callback`)**: After a successful `POST /token`, it stores `session["access_token"]` and redirects to `/profile`. It does not dump the raw token on the page anymore (that was only for display purpose in v03).
**2. Profile (`/profile`)**: It reads the token from session. If token is missing, it shows an error. Otherwise it calls `GET {AUTH_SERVER}/api/me` with the Bearer header (server-side, via `requests`). It renders username and email on success; or surfaces API errors on failure.
**3. Logout (`/logout`)**: This removes `access_token` from session and redirects home. The lab uses `GET` for simplicity; production apps would often prefer `POST` to avoid accidental logouts from prefetchers.[^logout-get]

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'actorLineColor': '#1e293b',
  'actorBorder': '#334155',
  'signalColor': '#1e293b',
  'lineColor': '#1e293b',
  'noteBorderColor': '#b45309',
  'noteBkgColor': '#fef9c3'
}}}%%
sequenceDiagram
    participant Browser as Browser
    box rgba(5,80,174,0.18) Client :25001
        participant ClientApp as OAuth Client
    end
    box rgba(196,30,58,0.18) Auth + Resource Server :25000
        participant AuthServer as Auth Server
    end

    Note over Browser,ClientApp: v03 legs: authorize, PKCE, token exchange
    Browser->>ClientApp: GET /callback?code=...&state=...
    ClientApp->>AuthServer: POST /token
    AuthServer->>ClientApp: access_token JSON
    Note over ClientApp: session["access_token"] = token
    ClientApp->>Browser: 302 /profile
    Browser->>ClientApp: GET /profile
    ClientApp->>AuthServer: GET /api/me<br/>Authorization: Bearer token
    Note over AuthServer: Validate token, load user
    AuthServer->>ClientApp: 200 user JSON
    ClientApp->>Browser: Profile page
```

### What changed from v03

| Piece | v03 | v04 |
|-------|-----|-----|
| Server | `POST /token` mints tokens | also `GET /api/me` validates Bearer tokens |
| Client `/callback` | renders `code`, `state`, `access_token` | stores token in session; redirects to `/profile` |
| Client routes | `/login`, `/callback`, `/` | adds `/profile`, `/logout` |
| Client `/` | static links | shows logged-in state via `/api/me` when session has a token |
| User storage | `users` had `password` + `user_id` | adds display `username` and `email` for the API response |

The authorization and token endpoints are unchanged. v04 is the first version where the access token does work after it is issued.

## How to run it

Two terminals (from [github.com/sauvikbiswas/oauth-lab](https://github.com/sauvikbiswas/oauth-lab)):

**Terminal 1: authorization + resource server**

```bash
cd versions/v04-protected-resource/server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../../../.env.example .env
python3 app.py
```

**Terminal 2: client**

```bash
cd versions/v04-protected-resource/client
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../../../.env.example .env
python3 app.py
```

Open `http://localhost:25001` and click **Start authorization**. Log in as `user0` / `password0`. You should land on `/profile` with a display name and email, not a raw token string.

### Negative tests

Since you can directly call the `/api/me` endpoint of the Resource Server, it's easy to test out some failure cases.

| Test | How | Expected |
|------|-----|----------|
| No Bearer header | `curl -s http://localhost:25000/api/me` | 401 |
| Fake token | `curl -s http://localhost:25000/api/me -H "Authorization: Bearer not-a-real-token"` | 401 |
| Profile without login | Visit `http://localhost:25001/profile` in a fresh session | Error: token missing from session |
| Logout | Click **Log out** on home or profile | `/profile` fails; home shows "Not logged in" |

Expired tokens are harder to demo without waiting an hour or editing `expires_at` in memory. The server checks `token_data["expires_at"] < datetime.now()` the same way it checks existence.

## What logout does not do

v04 logout clears the token from the client session only. The auth server still has the entry in `memory.access_tokens`. There is no revocation endpoint in the auth server. A copied token remains valid until expiry. That is fairly normal for real-world scenarios where "logout" means this app stops using the credential and is not treated as "invalidate everywhere." This is often acceptable as TTL of the token is typically short (5-15 mins).

## What the client should remember

v04 stores `access_token` in the Flask session and fetches profile from `/api/me` when you open `/profile` or the home page. That is session-scoped, not permanent storage; the cookie expires when the session ends.

Real apps often persist some user-related data, but the pattern depends on client type:

| What gets stored | How typical is it? | Why bother? |
|------------------|----------|-------------|
| Refresh token | Yes, if the app should stay signed in | When the access token expires, the app trades this for a new one at `POST /token` without opening the browser login page again (not yet implemented). |
| Access token | Sometimes, until it expires | The app sends this on API calls (`Authorization: Bearer …`) to prove you already logged in. Often kept in server session or memory, not forever on disk. |
| Profile fields (name, email, `user_id`) | Often | Display only: "Welcome, User Number 0." Can be cached locally; `/api/me` (or any protected API) still decides whether the token is valid. |
| App data (theme, drafts, settings) | Yes | This is the app's own state. OAuth does not define this. |

What is not usual is treating a cached profile as proof of identity without a valid token, or keeping access tokens forever without expiry, refresh, and secure storage.

## Cast of characters (v04 additions)

| Name | Who creates it | Where it travels | What it does |
|------|----------------|------------------|--------------|
| `Authorization: Bearer` | Client app | Client app to resource server (`GET /api/me`) | [RFC 6750](https://datatracker.ietf.org/doc/html/rfc6750) header carrying the access token. |
| `GET /api/me` | Resource server | Client app to auth server (same process in v04) | Protected API: validates Bearer token, returns user JSON. |
| `/profile` | Client app | Browser to client app | Profile page; fetches `/api/me` server-side with stored token. |
| `/logout` | Client app | Browser to client app | Clears `access_token` from client session (lab uses `GET`). |
| `username` / `email` | Pre-seeded on server | `GET /api/me` JSON response | Display fields added to `memory.users` for the API response. |

Parameters from v02–v03 (`state`, PKCE, `access_token`, `grant_type`) are unchanged.

## What next?

v04 completes the Authorization Code + PKCE loop through a protected API. I'll not work on deployment-style concerns (token revocation, database, splitting authorization and resource servers, error-page polish). There is one hard requirement that I'll address next. That is refresh tokens.

Diff adjacent snapshots:

```bash
diff -ru versions/v04-protected-resource versions/v05-refresh-token
```

[^logout-get]: **Why we should not use `GET /logout` in production:** A logout route changes state by clearing the session. HTTP convention treats `GET` as safe. i.e., clients may request a URL without the user explicitly meaning to act. Modern browsers prefetch linked pages to speed up navigation. Security scanners and mail clients sometimes fetch every URL in an email to check for malware. If logout is a `GET` link, one of those background requests can hit `/logout` and log you out even though you never clicked. A `POST` (usually a form with a button) is not prefetched the same way, so accidental logouts are much rarer. I have used `GET` anyway. One-line template is easier while learning OAuth. When you ship something real, use `POST` (or a server-side session cookie cleared via a form).

## Further reading

- [RFC 6750: The OAuth 2.0 Authorization Framework: Bearer Token Usage](https://datatracker.ietf.org/doc/html/rfc6750)
- [RFC 6749 §1.1: Roles](https://datatracker.ietf.org/doc/html/rfc6749#section-1.1)
- [RFC 6749 §7: Accessing Protected Resources](https://datatracker.ietf.org/doc/html/rfc6749#section-7)