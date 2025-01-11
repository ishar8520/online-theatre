CREATE SCHEMA IF NOT EXISTS auth;

CREATE TABLE IF NOT EXISTS auth.users (
    id uuid PRIMARY KEY,
    login text NOT NULL,
    password text,
    first_name text,
    last_name text,
    created timestamp without time zone,
    modified timestamp without time zone
);

CREATE INDEX IF NOT EXISTS ix_users_login ON auth.users(login);

CREATE TABLE IF NOT EXISTS auth.roles (
    id uuid PRIMARY KEY,
    name text NOT NULL,
    created timestamp without time zone,
    modified timestamp without time zone
);

CREATE INDEX IF NOT EXISTS ix_roles_name ON auth.roles(name);

CREATE TABLE IF NOT EXISTS auth.users_roles (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    role_id UUID NOT NULL,
    created timestamp with time zone,
    CONSTRAINT fk_role_id
        FOREIGN KEY (role_id)
        REFERENCES auth.roles (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_user_id
        FOREIGN KEY (user_id)
        REFERENCES auth.users(id)
        ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS uix_auth_role_id_user_id ON auth.users_roles(user_id, role_id);

CREATE TABLE IF NOT EXISTS auth.login_history (
    id uuid PRIMARY KEY,
    user_id UUID NOT NULL,
    user_agent text NOT NULL,
    created timestamp without time zone
);

CREATE INDEX IF NOT EXISTS ix_login_history_user_id ON auth.login_history(user_id);

