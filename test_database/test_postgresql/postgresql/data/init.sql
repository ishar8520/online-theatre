CREATE TABLE likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    movie_id VARCHAR(100) NOT NULL,
    rating INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    movie_id VARCHAR(100) NOT NULL,
    rating INT,
    text VARCHAR(200) NOT NULL,
    review_likes INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bookmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    movie_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
