'use strict';

const crypto = require('node:crypto');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'dev-only-insecure-secret-change-me';
const BCRYPT_COST = 10;
const TOKEN_TTL = '1h';
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// In-memory user store: email (lowercased) -> { id, email, passwordHash }
const users = new Map();

function isValidEmail(email) {
  return typeof email === 'string' && EMAIL_RE.test(email);
}

function isValidPassword(password) {
  return typeof password === 'string' && password.length >= 8;
}

function duplicateEmailError() {
  const err = new Error('Email already registered');
  err.status = 409;
  return err;
}

async function registerUser(email, password) {
  const key = email.toLowerCase();
  if (users.has(key)) {
    throw duplicateEmailError();
  }
  const passwordHash = await bcrypt.hash(password, BCRYPT_COST);
  // Re-check after the await: a concurrent registration may have won the race
  // while bcrypt was hashing (TOCTOU) — never overwrite the existing user.
  if (users.has(key)) {
    throw duplicateEmailError();
  }
  const user = { id: crypto.randomUUID(), email: key, passwordHash };
  users.set(key, user);
  return { id: user.id, email: user.email };
}

async function authenticate(email, password) {
  const user = users.get(String(email).toLowerCase());
  if (!user) return null;
  const ok = await bcrypt.compare(password, user.passwordHash);
  return ok ? user : null;
}

function issueToken(user) {
  return jwt.sign({ sub: user.id, email: user.email }, JWT_SECRET, {
    algorithm: 'HS256',
    expiresIn: TOKEN_TTL,
  });
}

function verifyToken(token) {
  return jwt.verify(token, JWT_SECRET, { algorithms: ['HS256'] });
}

function findUserById(id) {
  for (const user of users.values()) {
    if (user.id === id) return user;
  }
  return null;
}

module.exports = {
  users,
  isValidEmail,
  isValidPassword,
  registerUser,
  authenticate,
  issueToken,
  verifyToken,
  findUserById,
  JWT_SECRET,
};
