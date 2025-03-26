import logging
from uuid import UUID

import httpx
from fastapi import HTTPException, status

import logging

logging.basicConfig(level=logging.INFO)


class AuthClient:
    def __init__(self, auth_service_url: str):
        self.auth_service_url = auth_service_url

    async def verify_user(self, token: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                logging.info(f"{self.auth_service_url}/auth/api/v1/users/me")
                headers = {
                    "accept": "application/json",
                    "X-Request-ID": "123",
                    "Authorization": f"Bearer {token}"
                }
                response = await client.get(
                    f"{self.auth_service_url}/auth/api/v1/users/me",
                    headers=headers,
                    timeout=5.0
                )
                if response.status_code == status.HTTP_200_OK:
                    return response.text
                elif response.status_code == status.HTTP_401_UNAUTHORIZED:
                    raise HTTPException(
                        status.HTTP_401_UNAUTHORIZED,
                        detail="Unautorized",
                    )
                elif response.status_code == status.HTTP_400_BAD_REQUEST:
                    raise HTTPException(
                        status.HTTP_400_BAD_REQUEST,
                        detail="Bad Request",
                    )

        except httpx.RequestError as e:
            logging.info(f"Error connecting to auth service: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authorization service unavailable"
            )

auth_client = AuthClient(auth_service_url="http://auth-service:8000")
