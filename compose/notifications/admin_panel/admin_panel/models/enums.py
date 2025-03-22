import enum


class DeliveryEnum(enum.Enum):
    EMAIL = "email"
    # не используем, но предполагаем для будущей реализации
    MESSAGE = "message"
    TELEGRAM = "telegram"
    WEBSOCKET = "websocket"


class AdminNotificationTaskStatusEnum(enum.Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"


class AdminNotificationTypesEnum(enum.Enum):
    REGISTRATION = "registration"
    NEW_EPISODES = "new_episodes"
    NEW_FILMS = "new_films"
    NEWS = "news"
    PROMOTION = "promotion"
    MOVIE_RECOMMENDATION = "movies_recommendation"
    LIKE_NOTIFICATION = "likes_reviews"


class AdminNotificationStatusEnum(enum.Enum):
    CREATED = "created"
    SUCCESS = "success"
    FAILED = "failed"


class TemplateTypeEnum(enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    OTHER = "other"
