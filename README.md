# User Management

## Resource

**Users**

Attributes:

### Table: users
* email (string)
* firstname (string)
* lastname (string)
* phone (integer)
* passhash (string)


## Schema
```sql
CREATE TABLE users (
id INTEGER PRIMARY KEY,
email TEXT NOT NULL UNIQUE,
firstname TEXT NOT NULL,
lastname TEXT NOT NULL,
phone TEXT NOT NULL,
);
```

## Password Hashing
Passwords are hashed using Passlib's Argon2 implementation

## REST Endpoints

Name                           | Method | Path
-------------------------------|--------|------------------
Retrieve user collection      | GET    | /users
Retrieve user member          | GET    | /users/*\<id\>*
Create user member            | POST   | /users
Update user member            | PUT    | /users/*\<id\>*
Delete user member            | DELETE | /users/*\<id\>*
Check if session exists       | GET    | /sessions
Sign in user                  | POST   | /sessions
Live email validation         | POST   | /tools
