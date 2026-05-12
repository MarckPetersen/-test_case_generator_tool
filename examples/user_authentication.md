# User Authentication Requirements

## FR-001: User Registration

- New users can register with a unique email address and a password.
- Email must be a valid format (e.g., user@domain.com).
- Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one digit, and one special character.
- If the email is already registered, the system displays an error: "An account with this email already exists."
- On successful registration, the user receives a verification email and is redirected to a "Check your inbox" page.
- Unverified accounts cannot log in.

## FR-002: User Login

- Registered and verified users can log in using their email and password.
- After 5 consecutive failed login attempts, the account is locked for 15 minutes.
- A locked account displays: "Your account is temporarily locked. Try again in 15 minutes."
- On successful login, the user is redirected to the dashboard.
- A "Remember me" checkbox keeps the session active for 30 days.
- Sessions without "Remember me" expire after 1 hour of inactivity.

## FR-003: Password Reset

- Users can request a password reset from the login page by entering their email.
- A password reset link is sent to the registered email; it expires after 1 hour.
- Clicking an expired or already-used link shows: "This link has expired. Please request a new one."
- The new password must meet the same complexity rules as FR-001.
- After a successful reset, all other active sessions are invalidated.

## FR-004: Logout

- Authenticated users can log out via a "Logout" button available on all pages.
- Logging out invalidates the current session token immediately.
- After logout the user is redirected to the login page.
- Accessing a protected page after logout redirects to login (no cached content shown).
