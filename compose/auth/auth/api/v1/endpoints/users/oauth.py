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
    OAuthClientServiceDep,
    AuthenticationBackendDep,
    UserManagerDep,
    UserAlreadyExists,
)
from .....services.users.jwt import (
    generate_jwt,
    decode_jwt,
)

STATE_TOKEN_AUDIENCE = 'users:oauth-state:{provider_name}'

router = APIRouter()


class OAuth2AuthorizeResponse(BaseModel):
    authorization_url: str


@router.get(
    '/{provider_name}/authorize',
    name='oauth:authorize',
    response_model=OAuth2AuthorizeResponse,
)
async def authorize(*,
                    request: Request,
                    provider_name: str,
                    scope: list[str] | None = Query(None),
                    oauth_client_service: OAuthClientServiceDep) -> OAuth2AuthorizeResponse:
    oauth_client = oauth_client_service.create_client(provider_name)
    if oauth_client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    authorize_redirect_url = str(request.url_for('oauth:callback', provider_name=provider_name))
    audience = STATE_TOKEN_AUDIENCE.format(provider_name=provider_name)
    state = generate_jwt({
        'aud': audience,
    }, secret=settings.auth.secret_key)
    authorization_url = await oauth_client.get_authorization_url(
        authorize_redirect_url,
        state=state,
        scope=scope,
    )

    return OAuth2AuthorizeResponse(authorization_url=authorization_url)


@router.get(
    '/{provider_name}/callback',
    name='oauth:callback',
)
async def callback(*,
                   request: Request,
                   provider_name: str,
                   oauth_client_service: OAuthClientServiceDep,
                   code: str | None = Query(None),
                   code_verifier: str | None = Query(None),
                   state: str | None = Query(None),
                   error: str | None = Query(None),
                   user_manager: UserManagerDep,
                   backend: AuthenticationBackendDep):
    oauth_client = oauth_client_service.create_client(provider_name)
    if oauth_client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    audience = STATE_TOKEN_AUDIENCE.format(provider_name=provider_name)
    try:
        decode_jwt(state, secret=settings.auth.secret_key, audience=[audience])
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.OAUTH_INVALID_STATE_TOKEN,
        )

    authorize_callback_url = str(request.url_for('oauth:callback', provider_name=provider_name))
    oauth2_authorize_callback = OAuth2AuthorizeCallback(
        oauth_client,
        redirect_url=authorize_callback_url,
    )
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
