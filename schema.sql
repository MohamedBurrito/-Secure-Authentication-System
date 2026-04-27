CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,       -- الباك اند هيخزن الهاش هنا
    role TEXT NOT NULL,           -- (Admin, Manager, User)
    two_factor_secret TEXT        -- السيرفر هيخزن كود الـ 2FA هنا
);