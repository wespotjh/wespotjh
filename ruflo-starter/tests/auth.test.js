'use strict';

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const request = require('supertest');
const jwt = require('jsonwebtoken');

const app = require('../src/app');
const { JWT_SECRET } = require('../src/auth');

const EMAIL = 'alice@example.com';
const PASSWORD = 'correct-horse-battery';

describe('POST /auth/register', () => {
  test('registers a new user (201 with id and email)', async () => {
    const res = await request(app)
      .post('/auth/register')
      .send({ email: EMAIL, password: PASSWORD });
    assert.equal(res.status, 201);
    assert.equal(res.body.email, EMAIL);
    assert.ok(res.body.id);
    assert.equal(res.body.password, undefined);
    assert.equal(res.body.passwordHash, undefined);
  });

  test('rejects duplicate email (409)', async () => {
    const res = await request(app)
      .post('/auth/register')
      .send({ email: EMAIL, password: PASSWORD });
    assert.equal(res.status, 409);
  });

  test('rejects missing email (400)', async () => {
    const res = await request(app)
      .post('/auth/register')
      .send({ password: PASSWORD });
    assert.equal(res.status, 400);
  });

  test('rejects invalid email format (400)', async () => {
    const res = await request(app)
      .post('/auth/register')
      .send({ email: 'not-an-email', password: PASSWORD });
    assert.equal(res.status, 400);
  });

  test('rejects short password (400)', async () => {
    const res = await request(app)
      .post('/auth/register')
      .send({ email: 'bob@example.com', password: 'short' });
    assert.equal(res.status, 400);
  });

  test('rejects malformed JSON with a generic message (400)', async () => {
    const res = await request(app)
      .post('/auth/register')
      .set('Content-Type', 'application/json')
      .send('{bad');
    assert.equal(res.status, 400);
    assert.deepEqual(res.body, { error: 'Invalid request body' });
  });
});

describe('POST /auth/login', () => {
  test('returns a verifiable JWT on success (200)', async () => {
    const res = await request(app)
      .post('/auth/login')
      .send({ email: EMAIL, password: PASSWORD });
    assert.equal(res.status, 200);
    assert.ok(res.body.token);

    const payload = jwt.verify(res.body.token, JWT_SECRET, {
      algorithms: ['HS256'],
    });
    assert.equal(payload.email, EMAIL);
    assert.ok(payload.sub);
    assert.ok(payload.exp - payload.iat === 3600, 'token expires in 1h');
  });

  test('rejects wrong password (401)', async () => {
    const res = await request(app)
      .post('/auth/login')
      .send({ email: EMAIL, password: 'wrong-password-123' });
    assert.equal(res.status, 401);
  });

  test('rejects unknown email with the same message (401)', async () => {
    const wrongPw = await request(app)
      .post('/auth/login')
      .send({ email: EMAIL, password: 'wrong-password-123' });
    const unknown = await request(app)
      .post('/auth/login')
      .send({ email: 'nobody@example.com', password: PASSWORD });
    assert.equal(unknown.status, 401);
    assert.deepEqual(unknown.body, wrongPw.body);
  });

  test('rejects missing fields (400)', async () => {
    const res = await request(app).post('/auth/login').send({ email: EMAIL });
    assert.equal(res.status, 400);
  });
});

describe('GET /me', () => {
  async function loginToken() {
    const res = await request(app)
      .post('/auth/login')
      .send({ email: EMAIL, password: PASSWORD });
    return res.body.token;
  }

  test('returns the current user with a valid token (200)', async () => {
    const token = await loginToken();
    const res = await request(app)
      .get('/me')
      .set('Authorization', `Bearer ${token}`);
    assert.equal(res.status, 200);
    assert.equal(res.body.email, EMAIL);
    assert.ok(res.body.id);
  });

  test('rejects a missing Authorization header (401)', async () => {
    const res = await request(app).get('/me');
    assert.equal(res.status, 401);
  });

  test('rejects a malformed Authorization header (401)', async () => {
    const token = await loginToken();
    const res = await request(app).get('/me').set('Authorization', token);
    assert.equal(res.status, 401);
  });

  test('rejects an invalid token (401)', async () => {
    const res = await request(app)
      .get('/me')
      .set('Authorization', 'Bearer not.a.token');
    assert.equal(res.status, 401);
  });

  test('rejects a valid token whose sub maps to no stored user (401)', async () => {
    const ghost = jwt.sign(
      { sub: 'no-such-user-id', email: 'ghost@example.com' },
      JWT_SECRET,
      { algorithm: 'HS256', expiresIn: '1h' }
    );
    const res = await request(app)
      .get('/me')
      .set('Authorization', `Bearer ${ghost}`);
    assert.equal(res.status, 401);
  });

  test('rejects an expired token (401)', async () => {
    const expired = jwt.sign(
      { sub: 'some-id', email: EMAIL },
      JWT_SECRET,
      { algorithm: 'HS256', expiresIn: '-1s' }
    );
    const res = await request(app)
      .get('/me')
      .set('Authorization', `Bearer ${expired}`);
    assert.equal(res.status, 401);
  });
});
