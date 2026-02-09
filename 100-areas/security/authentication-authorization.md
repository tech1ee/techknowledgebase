---
title: "Authentication & Authorization: кто ты и что тебе можно"
created: 2025-11-24
modified: 2025-11-24
type: concept
status: published
confidence: high
sources_verified: true
tags:
  - topic/security
  - security/auth
  - security/oauth
  - security/jwt
  - type/concept
  - level/intermediate
related:
  - "[[web-security-owasp]]"
  - "[[api-design]]"
  - "[[microservices-vs-monolith]]"
  - "[[network-dns-tls]]"
---

# Authentication & Authorization: кто ты и что тебе можно

AuthN = "Кто ты?" (логин, OAuth). AuthZ = "Что тебе можно?" (роли, permissions). "Залогинен" ≠ "Может это делать" — проверка AuthN без AuthZ = Broken Access Control (#1 OWASP).

---

## Терминология

| Термин | Значение |
|--------|----------|
| **AuthN** | Authentication — проверка личности |
| **AuthZ** | Authorization — проверка прав |
| **Session** | Stateful аутентификация (сервер хранит состояние) |
| **JWT** | JSON Web Token — stateless токен |
| **OAuth 2.0** | Протокол делегирования доступа |
| **OIDC** | OpenID Connect — identity layer над OAuth |
| **MFA/2FA** | Multi/Two Factor Authentication |
| **RBAC** | Role-Based Access Control — доступ по ролям |
| **ABAC** | Attribute-Based Access Control — доступ по атрибутам |

---

## AuthN vs AuthZ: разница критична

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  AUTHENTICATION (AuthN)          AUTHORIZATION (AuthZ)         │
│  ─────────────────────          ──────────────────────         │
│                                                                 │
│  "КТО ты?"                      "ЧТО тебе можно?"              │
│                                                                 │
│  • Логин + пароль               • Роли (admin, user)           │
│  • OAuth (Google, GitHub)       • Permissions (read, write)    │
│  • Биометрия                    • Policies (ABAC, RBAC)        │
│  • 2FA/MFA                      • Scopes (API доступ)          │
│                                                                 │
│  Результат: Identity            Результат: Да/Нет на действие  │
│  "Это точно Вася"               "Вася может удалять посты"     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Типичная ошибка:
"Пользователь залогинен" ≠ "Пользователь может это делать"

Проверка AuthN без AuthZ = Broken Access Control (#1 OWASP)
```

---

## Способы аутентификации

### Sessions (stateful)

```
┌──────────┐      1. Login         ┌──────────┐
│  Browser │ ──────────────────────▶│  Server  │
│          │   email + password    │          │
│          │                       │          │
│          │◀────────────────────── │          │
│          │  2. Set-Cookie:       │  Session │
│          │     sessionId=abc123  │  Store   │
│          │                       │  {abc123 │
│          │  3. Каждый запрос     │   → user}│
│          │ ──────────────────────▶│          │
│          │  Cookie: sessionId    │          │
└──────────┘                       └──────────┘

Плюсы:
+ Можно отозвать сессию мгновенно
+ Сервер контролирует состояние
+ Простая реализация

Минусы:
- Хранилище сессий (Redis, DB)
- Sticky sessions при масштабировании
- CSRF уязвимость (нужен токен)
```

```typescript
// Express + express-session
import session from 'express-session';
import RedisStore from 'connect-redis';

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,        // Только HTTPS
    httpOnly: true,      // Недоступно из JS
    sameSite: 'strict',  // CSRF защита
    maxAge: 24 * 60 * 60 * 1000  // 24 часа
  }
}));

// Логин
app.post('/login', async (req, res) => {
  const user = await authenticate(req.body.email, req.body.password);
  if (user) {
    req.session.userId = user.id;
    req.session.role = user.role;
    res.json({ success: true });
  } else {
    res.status(401).json({ error: 'Invalid credentials' });
  }
});

// Проверка
function requireAuth(req, res, next) {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  next();
}

// Логаут — мгновенное завершение
app.post('/logout', (req, res) => {
  req.session.destroy();
  res.json({ success: true });
});
```

### JWT (stateless)

```
┌──────────┐      1. Login         ┌──────────┐
│  Client  │ ──────────────────────▶│  Server  │
│          │   email + password    │          │
│          │                       │          │
│          │◀────────────────────── │          │
│          │  2. JWT Token         │ Нет      │
│          │                       │ хранилища│
│          │  3. Authorization:    │          │
│          │     Bearer <token>    │          │
│          │ ──────────────────────▶│          │
│          │  Сервер проверяет     │          │
│          │  подпись, не хранит   │          │
└──────────┘                       └──────────┘
```

```
JWT структура:

Header.Payload.Signature

┌─────────────────────────────────────────────────────┐
│ Header (Base64)                                     │
│ {"alg": "HS256", "typ": "JWT"}                      │
├─────────────────────────────────────────────────────┤
│ Payload (Base64) — НЕ ЗАШИФРОВАНО!                  │
│ {                                                   │
│   "sub": "user_123",      // Subject (user ID)      │
│   "email": "user@ex.com", // Custom claims          │
│   "role": "admin",                                  │
│   "iat": 1700000000,      // Issued at              │
│   "exp": 1700086400       // Expiration             │
│ }                                                   │
├─────────────────────────────────────────────────────┤
│ Signature                                           │
│ HMAC-SHA256(header + payload, secret)               │
│ или RS256 (асимметричная подпись)                   │
└─────────────────────────────────────────────────────┘

⚠️  Payload видно всем! Не храни секреты в JWT
```

```typescript
// JWT реализация
import jwt from 'jsonwebtoken';

const ACCESS_TOKEN_SECRET = process.env.ACCESS_SECRET;
const REFRESH_TOKEN_SECRET = process.env.REFRESH_SECRET;

// Генерация токенов
function generateTokens(user: User) {
  const accessToken = jwt.sign(
    {
      sub: user.id,
      email: user.email,
      role: user.role
    },
    ACCESS_TOKEN_SECRET,
    { expiresIn: '15m' }  // Короткий срок!
  );

  const refreshToken = jwt.sign(
    { sub: user.id },
    REFRESH_TOKEN_SECRET,
    { expiresIn: '7d' }
  );

  return { accessToken, refreshToken };
}

// Middleware проверки
function authenticateToken(req, res, next) {
  const authHeader = req.headers.authorization;
  const token = authHeader?.split(' ')[1];  // "Bearer <token>"

  if (!token) {
    return res.status(401).json({ error: 'Token required' });
  }

  try {
    const payload = jwt.verify(token, ACCESS_TOKEN_SECRET);
    req.user = payload;
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Token expired' });
    }
    return res.status(403).json({ error: 'Invalid token' });
  }
}

// Refresh endpoint
app.post('/refresh', async (req, res) => {
  const { refreshToken } = req.body;

  try {
    const payload = jwt.verify(refreshToken, REFRESH_TOKEN_SECRET);

    // Проверить, не отозван ли refresh token (blacklist)
    const isRevoked = await checkTokenBlacklist(refreshToken);
    if (isRevoked) {
      return res.status(403).json({ error: 'Token revoked' });
    }

    const user = await getUserById(payload.sub);
    const tokens = generateTokens(user);

    res.json(tokens);
  } catch (error) {
    res.status(403).json({ error: 'Invalid refresh token' });
  }
});
```

```
JWT: Плюсы и минусы

Плюсы:
+ Stateless — не нужно хранилище
+ Масштабируется горизонтально
+ Работает между сервисами (микросервисы)
+ Payload содержит данные (меньше запросов к БД)

Минусы:
- НЕЛЬЗЯ отозвать до истечения срока
- Размер больше session ID
- Payload не зашифрован (только подписан)
- Сложнее refresh логика
```

---

## OAuth 2.0: делегирование доступа

```
Зачем OAuth:

Без OAuth:
"Дай мне пароль от Google, я проверю твою почту"
→ Пользователь даёт пароль третьему сервису
→ Сервис имеет ПОЛНЫЙ доступ
→ Нельзя отозвать без смены пароля

С OAuth:
"Разреши мне читать твой email через Google"
→ Пользователь авторизует на сайте Google
→ Сервис получает ограниченный токен
→ Можно отозвать в любой момент
```

### Authorization Code Flow (для веб-приложений)

```
┌──────────┐                              ┌──────────┐
│   User   │                              │  Google  │
│ Browser  │                              │  (IdP)   │
└────┬─────┘                              └────┬─────┘
     │                                         │
     │  1. Клик "Login with Google"            │
     │─────────────────────────────────────────▶
     │     /authorize?                         │
     │       client_id=xxx                     │
     │       redirect_uri=https://app/callback │
     │       scope=email profile               │
     │       state=random123                   │
     │                                         │
     │  2. Логин в Google (если не залогинен)  │
     │◀─────────────────────────────────────────
     │     "Разрешить App доступ к email?"     │
     │                                         │
     │  3. Redirect обратно с code             │
     │◀─────────────────────────────────────────
     │     https://app/callback?               │
     │       code=AUTH_CODE                    │
     │       state=random123                   │
     │                                         │
┌────┴─────┐                              ┌────┴─────┐
│   App    │  4. Обмен code на tokens     │  Google  │
│  Server  │─────────────────────────────▶│   API    │
│          │     POST /token               │          │
│          │     code=AUTH_CODE            │          │
│          │     client_secret=xxx         │          │
│          │                               │          │
│          │◀─────────────────────────────│          │
│          │  5. access_token,             │          │
│          │     refresh_token,            │          │
│          │     id_token (OIDC)           │          │
│          │                               │          │
│          │  6. Запрос данных пользователя│          │
│          │─────────────────────────────▶│          │
│          │     GET /userinfo             │          │
│          │     Authorization: Bearer xxx │          │
└──────────┘                              └──────────┘
```

```typescript
// OAuth с Passport.js
import passport from 'passport';
import { Strategy as GoogleStrategy } from 'passport-google-oauth20';

passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: '/auth/google/callback'
  },
  async (accessToken, refreshToken, profile, done) => {
    // Найти или создать пользователя
    let user = await User.findOne({ googleId: profile.id });

    if (!user) {
      user = await User.create({
        googleId: profile.id,
        email: profile.emails[0].value,
        name: profile.displayName,
        avatar: profile.photos[0]?.value
      });
    }

    return done(null, user);
  }
));

// Routes
app.get('/auth/google',
  passport.authenticate('google', { scope: ['profile', 'email'] })
);

app.get('/auth/google/callback',
  passport.authenticate('google', { failureRedirect: '/login' }),
  (req, res) => {
    // Успешная аутентификация
    const token = generateTokens(req.user);
    res.redirect(`/app?token=${token.accessToken}`);
  }
);
```

### OAuth Flows: когда какой

```
┌─────────────────────────────────────────────────────────────────┐
│                      OAUTH 2.0 FLOWS                            │
├──────────────────────┬──────────────────────────────────────────┤
│ Authorization Code   │ Веб-приложения с backend                 │
│                      │ ✓ Безопасно (secret на сервере)          │
├──────────────────────┼──────────────────────────────────────────┤
│ Authorization Code   │ SPA, мобильные приложения                │
│ + PKCE               │ ✓ Без client_secret                      │
│                      │ ✓ Защита от перехвата code               │
├──────────────────────┼──────────────────────────────────────────┤
│ Client Credentials   │ Сервис-к-сервису (M2M)                   │
│                      │ ✓ Нет пользователя                       │
├──────────────────────┼──────────────────────────────────────────┤
│ ⚠️ Implicit          │ УСТАРЕЛ! Не использовать                 │
│                      │ ✗ Token в URL = небезопасно              │
├──────────────────────┼──────────────────────────────────────────┤
│ ⚠️ Password Grant    │ УСТАРЕЛ! Только legacy                   │
│                      │ ✗ Пароль передаётся приложению           │
└──────────────────────┴──────────────────────────────────────────┘
```

---

## Authorization: RBAC vs ABAC

### RBAC (Role-Based Access Control)

```typescript
// Простой RBAC
const permissions = {
  admin: ['read', 'write', 'delete', 'manage_users'],
  editor: ['read', 'write'],
  viewer: ['read']
};

function checkPermission(user: User, action: string): boolean {
  const userPermissions = permissions[user.role] || [];
  return userPermissions.includes(action);
}

// Middleware
function requirePermission(action: string) {
  return (req, res, next) => {
    if (!checkPermission(req.user, action)) {
      return res.status(403).json({ error: 'Forbidden' });
    }
    next();
  };
}

// Использование
app.delete('/posts/:id',
  authenticateToken,
  requirePermission('delete'),
  deletePost
);
```

### ABAC (Attribute-Based Access Control)

```typescript
// ABAC — более гибкий подход
interface AccessContext {
  user: User;
  resource: Resource;
  action: string;
  environment: {
    time: Date;
    ip: string;
  };
}

// Политики как функции
type Policy = (context: AccessContext) => boolean;

const policies: Policy[] = [
  // Автор может редактировать свои посты
  (ctx) => ctx.action === 'edit' && ctx.resource.authorId === ctx.user.id,

  // Админ может всё
  (ctx) => ctx.user.role === 'admin',

  // Редактор может редактировать в рабочее время
  (ctx) => {
    if (ctx.user.role !== 'editor') return false;
    const hour = ctx.environment.time.getHours();
    return hour >= 9 && hour <= 18;
  },

  // Публичные ресурсы может читать кто угодно
  (ctx) => ctx.action === 'read' && ctx.resource.isPublic
];

function checkAccess(context: AccessContext): boolean {
  return policies.some(policy => policy(context));
}

// Использование
app.put('/posts/:id', authenticateToken, async (req, res) => {
  const post = await Post.findById(req.params.id);

  const canAccess = checkAccess({
    user: req.user,
    resource: post,
    action: 'edit',
    environment: { time: new Date(), ip: req.ip }
  });

  if (!canAccess) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  // Обновить пост
});
```

```
RBAC vs ABAC:

RBAC:
+ Простой в реализации
+ Легко понять и аудитировать
- Негибкий (нужны новые роли для каждого случая)
- "Role explosion" при сложных правилах

ABAC:
+ Очень гибкий
+ Контекстные правила (время, место, ресурс)
- Сложнее реализовать
- Сложнее аудитировать

Рекомендация: начни с RBAC, перейди на ABAC когда появятся
сложные правила типа "автор может редактировать свои посты"
```

---

## Безопасное хранение паролей

```typescript
// НИКОГДА так:
const passwordHash = md5(password);        // ❌ Слабый алгоритм
const passwordHash = sha256(password);     // ❌ Быстрый = плохо
const passwordHash = sha256(password + salt); // ❌ Всё ещё быстро

// ПРАВИЛЬНО: bcrypt, scrypt, или Argon2
import bcrypt from 'bcrypt';

const SALT_ROUNDS = 12;  // Увеличивать со временем

async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

// При регистрации
const hashedPassword = await hashPassword(userData.password);
await User.create({ email, password: hashedPassword });

// При логине
const user = await User.findByEmail(email);
const isValid = await verifyPassword(password, user.password);
```

```
Почему bcrypt/Argon2:

MD5/SHA:
  1 миллиард хешей в секунду на GPU
  = Весь словарь паролей за минуты

bcrypt (cost=12):
  ~3 хеша в секунду на CPU
  = Годы на перебор словаря

Argon2 (победитель Password Hashing Competition):
  + Защита от GPU атак (memory-hard)
  + Настраиваемые параметры
  + Рекомендуется для новых проектов
```

---

## Подводные камни

### Проблема 1: JWT без возможности отзыва

```
Сценарий:
1. Пользователь получил JWT (exp: 1 час)
2. Украли токен
3. Хотим заблокировать пользователя
4. JWT работает ещё 59 минут!

Решения:

1. Короткий срок жизни access token (15 мин)
   + refresh token для обновления
   + blacklist для refresh tokens

2. Token versioning
   User { tokenVersion: 5 }
   JWT { sub: userId, version: 5 }
   При логауте: user.tokenVersion++
   При проверке: сравнить версии

3. Гибрид: JWT + Redis check
   При каждом запросе проверять в Redis
   (теряем stateless преимущество)
```

### Проблема 2: Хранение токенов на клиенте

```
Где хранить токены в браузере:

localStorage:
  ❌ Доступен из JavaScript
  ❌ XSS = украден токен

sessionStorage:
  ❌ То же, что localStorage
  ❌ Теряется при закрытии вкладки

Cookie (httpOnly):
  ✅ Недоступен из JavaScript
  ✅ Автоматически отправляется
  ⚠️  Нужна CSRF защита

Рекомендация для SPA:
  • Access token: в памяти (переменная)
  • Refresh token: httpOnly cookie
  • При F5: запрос /refresh с cookie
```

### Проблема 3: OAuth state parameter

```
Без state параметра:

Атакующий:
1. Начинает OAuth flow на своём компьютере
2. Получает authorization URL
3. Отправляет жертве ссылку
4. Жертва кликает, авторизуется
5. Callback приходит на аккаунт атакующего
   привязанный к профилю жертвы!

С state:
1. Сервер генерирует random state
2. Сохраняет в session
3. При callback проверяет state
4. Если не совпадает → отказ

// Правильно
const state = crypto.randomBytes(32).toString('hex');
req.session.oauthState = state;
res.redirect(`${authUrl}&state=${state}`);

// В callback
if (req.query.state !== req.session.oauthState) {
  throw new Error('Invalid state');
}
```

---

## Чеклист безопасности

```
□ Пароли хешируются bcrypt/Argon2 (cost ≥ 12)
□ HTTPS везде (включая dev)
□ Cookies: httpOnly, secure, sameSite
□ JWT: короткий срок, проверка подписи
□ OAuth: state параметр, PKCE для SPA
□ Rate limiting на login endpoint
□ Нет паролей в логах
□ Нет секретов в коде (используй env)
□ 2FA для критичных операций
□ Password reset через email, не security questions
```

---

## Связи

- OWASP уязвимости: [[web-security-owasp]]
- Безопасность API: [[api-design]]
- Auth в микросервисах: [[microservices-vs-monolith]]

---

## Источники

- [OWASP: Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) — проверено 2025-11-24
- [Auth0: OAuth 2.0 Flows](https://auth0.com/docs/get-started/authentication-and-authorization-flow) — проверено 2025-11-24
- [RFC 6749: OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749) — проверено 2025-11-24
- [JWT.io: Introduction to JWT](https://jwt.io/introduction) — проверено 2025-11-24

---

**Последняя верификация**: 2025-11-24
**Уровень достоверности**: high

---

*Проверено: 2026-01-09*
