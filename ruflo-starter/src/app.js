'use strict';

const express = require('express');
const auth = require('./auth');

const app = express();
app.use(express.json());

const INVALID_CREDENTIALS = 'Invalid email or password';

app.post('/auth/register', async (req, res, next) => {
  try {
    const { email, password } = req.body || {};
    if (!auth.isValidEmail(email)) {
      return res.status(400).json({ error: 'A valid email is required' });
    }
    if (!auth.isValidPassword(password)) {
      return res
        .status(400)
        .json({ error: 'Password must be at least 8 characters' });
    }
    const user = await auth.registerUser(email, password);
    return res.status(201).json(user);
  } catch (err) {
    if (err.status === 409) {
      return res.status(409).json({ error: 'Email already registered' });
    }
    return next(err);
  }
});

app.post('/auth/login', async (req, res, next) => {
  try {
    const { email, password } = req.body || {};
    if (typeof email !== 'string' || typeof password !== 'string') {
      return res.status(400).json({ error: 'Email and password are required' });
    }
    const user = await auth.authenticate(email, password);
    if (!user) {
      return res.status(401).json({ error: INVALID_CREDENTIALS });
    }
    return res.status(200).json({ token: auth.issueToken(user) });
  } catch (err) {
    return next(err);
  }
});

app.get('/me', (req, res) => {
  const header = req.get('authorization') || '';
  const [scheme, token, ...rest] = header.split(' ');
  if (scheme !== 'Bearer' || !token || rest.length > 0) {
    return res.status(401).json({ error: 'Missing or malformed Authorization header' });
  }
  let payload;
  try {
    payload = auth.verifyToken(token);
  } catch {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
  const user = auth.findUserById(payload.sub);
  if (!user) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
  return res.status(200).json({ id: user.id, email: user.email });
});

// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  const status = err.status || (err.type === 'entity.parse.failed' ? 400 : 500);
  // Never echo err.message: body-parser errors reflect attacker-controlled bytes.
  res
    .status(status)
    .json({ error: status === 500 ? 'Internal server error' : 'Invalid request body' });
});

module.exports = app;
