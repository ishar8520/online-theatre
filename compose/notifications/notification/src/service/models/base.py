from __future__ import annotations

import enum


class NotificationType(enum.StrEnum):
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'
