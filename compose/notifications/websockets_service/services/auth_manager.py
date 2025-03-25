import logging
from uuid import UUID

import httpx
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class AuthClient:
    def __init__(self, auth_service_url: str):
        self.auth_service_url = auth_service_url

    async def verify_user(self, user_uuid: UUID) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.auth_service_url}/auth/api/v1/users/{user_uuid}/profile", timeout=5.0
                )
                if response.status_code == status.HTTP_200_OK:
                    return True
                elif response.status_code == status.HTTP_404_NOT_FOUND:
                    return False
                response.raise_for_status()
        except httpx.RequestError as e:
            logger.error(f"Error connecting to auth service: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authorization service unavailable"
            )


auth_client = AuthClient(auth_service_url="http://auth-service:8000")
