CREATE DATABASE IF NOT EXISTS ugc;

CREATE TABLE IF NOT EXISTS ugc.click(
    id UUID DEFAULT generateUUIDv4(),
    user_id UUID,
    element String,
    timestamp DateTime
) Engine=MergeTree() ORDER BY id;

CREATE TABLE IF NOT EXISTS ugc.page_view(
    id UUID DEFAULT generateUUIDv4(),
    user_id UUID,
    url String,
    duration String,
    timestamp DateTime
) Engine=MergeTree() ORDER BY id;

CREATE TABLE IF NOT EXISTS ugc.custom_event(
    id UUID DEFAULT generateUUIDv4(),
    user_id UUID,
    event_type String,
    movie_quality Nullable(String),
    movie_id Nullable(String),
    filters Nullable(String),
    timestamp DateTime
) Engine=MergeTree() ORDER BY id;
