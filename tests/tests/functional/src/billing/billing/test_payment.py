from __future__ import annotations

import datetime
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

            assert "id" in data_cancel
            assert data_cancel["id"] == data["id"]


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
                "status": http.HTTPStatus.OK,
                "url": "https://your_link_to_pay"
            }
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_payment_init_payment(
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

        payload = {
            "payment_method": "yoomoney"
        }

        url = urljoin(settings.url_billing_api, f"payment/init_payment/{data["id"]}")
        async with aiohttp_session.post(url, headers=auth_headers, json=payload) as response_init:
            assert response_init.status == expected["status"]

            data_init = await response_init.json()

            assert "url" in data_init
            assert data_init["url"] == expected["url"]


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
                "status": http.HTTPStatus.OK,
                "url": "https://your_link_to_refund"
            }
        )
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_payment_refund(
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

    payload = {
        "service": "yoomoney",
        "status": "success",
        "label": data["id"],
        "amount": payment_items[0]["price"],
        "withdraw_amount": payment_items[0]["price"],
        "datetime": datetime.datetime.now(datetime.UTC).isoformat()
    }

    url = urljoin(settings.url_billing_api, f"payment/process/{data["id"]}")
    async with aiohttp_session.post(url, headers=auth_headers, json=payload) as response_process:
        assert response_process.status == http.HTTPStatus.OK

        data_process = await response_process.json()

        assert "id" in data_process

    payload = {
        "payment_method": "yoomoney",
    }

    url = urljoin(settings.url_billing_api, f"payment/refund/{data["id"]}")
    async with aiohttp_session.post(url, headers=auth_headers, json=payload) as response_refund:
        assert response_refund.status == expected["status"]

        data_refund = await response_refund.json()

        assert "url" in data_refund
        assert data_refund["url"] == expected["url"]
