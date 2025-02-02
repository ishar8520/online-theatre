from __future__ import annotations

from http import HTTPStatus
from fastapi import HTTPException
from typing import Annotated
from fastapi import Depends

from .model.user import User
from .transport.exceptions import ResponseJsonError, RequestError

from ...core import settings
from .transport.http_async import HttpAsyncDep


async def get_auth_user(http_async: HttpAsyncDep):
    try:
        json = await http_async.get(settings.auth.url_me)
        if 'detail' in json:
            if json['detail'] == 'Unauthorized':
                raise HTTPException(HTTPStatus.UNAUTHORIZED)
            elif json['detail'] == 'Forbidden':
                raise HTTPException(HTTPStatus.FORBIDDEN)

        return User(**json)
    except ResponseJsonError:
        raise HTTPException(HTTPStatus.FORBIDDEN)
    except RequestError:
        raise HTTPException(HTTPStatus.SERVICE_UNAVAILABLE)

AuthUserDep = Annotated[User, Depends(get_auth_user)]
