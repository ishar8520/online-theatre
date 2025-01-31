from __future__ import annotations

import jwt
from fastapi import APIRouter, HTTPException, Query, Request, status
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from pydantic import BaseModel

from .common import (
    ErrorCode,
)
from .....core import settings
from .....services.users import (
    OAuthClientDep,
    AuthenticationBackendDep,
    UserManagerDep,
    UserAlreadyExists,
)
from .....services.users.jwt import (
    generate_jwt,
    decode_jwt,
)

STATE_TOKEN_AUDIENCE = 'users:oauth-state'

router = APIRouter()


class OAuth2AuthorizeResponse(BaseModel):
    authorization_url: str


@router.get(
    '/authorize',
    name='oauth:authorize',
    response_model=OAuth2AuthorizeResponse,
)
async def authorize(*,
                    request: Request,
                    scope: list[str] | None = Query(None),
                    oauth_client: OAuthClientDep) -> OAuth2AuthorizeResponse:
    authorize_redirect_url = str(request.url_for('oauth:callback'))
    state_data = {
        'aud': STATE_TOKEN_AUDIENCE,
    }
    state = generate_jwt(state_data, secret=settings.auth.secret_key)
    authorization_url = await oauth_client.get_authorization_url(
        authorize_redirect_url,
        state=state,
        scope=scope,
    )

    return OAuth2AuthorizeResponse(authorization_url=authorization_url)


@router.get(
    '/callback',
    name='oauth:callback',
)
async def callback(*,
                   request: Request,
                   oauth_client: OAuthClientDep,
                   code: str | None = Query(None),
                   code_verifier: str | None = Query(None),
                   state: str | None = Query(None),
                   error: str | None = Query(None),
                   user_manager: UserManagerDep,
                   backend: AuthenticationBackendDep):
    try:
        decode_jwt(state, secret=settings.auth.secret_key, audience=[STATE_TOKEN_AUDIENCE])
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.OAUTH_INVALID_STATE_TOKEN,
        )

    oauth2_authorize_callback = OAuth2AuthorizeCallback(oauth_client, route_name='oauth:callback')
    token, state = await oauth2_authorize_callback(
        request,
        code=code,
        code_verifier=code_verifier,
        state=state,
        error=error,
    )

    account_id, account_email = await oauth_client.get_id_email(token['access_token'])

    if account_email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.OAUTH_EMAIL_NOT_AVAILABLE,
        )

    try:
        user = await user_manager.oauth_callback(
            oauth_name=oauth_client.name,
            access_token=token['access_token'],
            account_id=account_id,
            account_email=account_email,
            expires_at=token.get('expires_at'),
            refresh_token=token.get('refresh_token'),
        )
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.OAUTH_USER_ALREADY_EXISTS,
        )

    return await backend.login(user)
