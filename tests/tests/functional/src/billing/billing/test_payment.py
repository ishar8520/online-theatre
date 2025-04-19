from __future__ import annotations

import http
from urllib.parse import urljoin

import pytest

from ....settings import settings


@pytest.mark.parametrize(
    "payment_items, expected",
    [
        (
            [
                {
                    "name": "Yandex Music",
                    "quantity": 1,
                    "price": 1000,
                    "type": "subscribe",
                    "props": [
                        {
                            "name": "Period",
                            "code": "period",
                            "value": "12"
                        }
                    ]
                }
            ],
            {
                "status": http.HTTPStatus.CREATED
            }
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_payment_create(
        aiohttp_session,
        auth_headers,
        payment_items,
        expected
):
    url = urljoin(settings.url_billing_api, f"payment/create")
    async with aiohttp_session.put(url, headers=auth_headers, json=payment_items) as response:
        assert response.status == expected["status"]

        data = await response.json()
        assert "id" in data


@pytest.mark.parametrize(
    "payment_items, expected",
    [
        (
            [
                {
                    "name": "Yandex Music",
                    "quantity": 1,
                    "price": 1000,
                    "type": "subscribe",
                    "props": [
                        {
                            "name": "Period",
                            "code": "period",
                            "value": "12"
                        }
                    ]
                }
            ],
            {
                "status": http.HTTPStatus.UNAUTHORIZED
            }
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_payment_create_without_auth(
        aiohttp_session,
        payment_items,
        expected
):
    url = urljoin(settings.url_billing_api, f"payment/create")
    async with aiohttp_session.put(url, json=payment_items) as response:
        assert response.status == expected["status"]


@pytest.mark.parametrize(
    "payment_items, expected",
    [
        (
            [
                {
                    "name": "Yandex Music",
                    "quantity": 1,
                    "price": 1000,
                    "type": "subscribe",
                    "props": [
                        {
                            "name": "Period",
                            "code": "period",
                            "value": "12"
                        }
                    ]
                }
            ],
            {
                "status": http.HTTPStatus.OK
            }
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_payment_cancel(
        aiohttp_session,
        auth_headers,
        payment_items,
        expected
):
    url = urljoin(settings.url_billing_api, f"payment/create")
    async with aiohttp_session.put(url, headers=auth_headers, json=payment_items) as response:
        assert response.status == http.HTTPStatus.CREATED

        data = await response.json()
        assert "id" in data

        url = urljoin(settings.url_billing_api, f"payment/cancel/{data["id"]}")
        async with aiohttp_session.post(url, headers=auth_headers) as response_cancel:
            assert response_cancel.status == expected["status"]

            data_cancel = await response.json()

            assert "id" in data
            assert data_cancel["id"] == data["id"]
