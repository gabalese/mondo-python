from decimal import Decimal as D

import datetime

import asyncio

import aiohttp
import dateutil.parser
import requests

from mondo import authorization
from mondo.exceptions import MondoApiException
from mondo.utils import build_url


class MondoApi(object):
    BASE_API_URL = 'https://api.getmondo.co.uk'

    def __init__(self, access_token: str):
        """
        :param access_token: The access token, as returned by the OAuth dance
        """
        self._access_token = access_token

    def _make_request(self, url: str, parameters: dict = None,
                      method: str = 'GET', *args, **kwargs):
        """
        Shortcut for a generic request to the mondo API

        :param url: The URL resource part
        :param parameters: Querystring parameters
        :param method: REST method
        :return: requests.Response
        """
        response = requests.request(
            method=method,
            url=build_url(
                self.BASE_API_URL, url, parameters
            ),
            headers={
                'Authorization': 'Bearer {}'.format(self._access_token)
            }, **kwargs
        )
        if response.ok:
            return response.json()
        raise MondoApiException(response.json()['message'])

    async def _make_async_request(self, url, parameters, method='GET',
                                  *args, **kwargs):

        loop = asyncio.get_event_loop()
        with aiohttp.ClientSession(loop=loop) as session:
            response = await session.request(
                method=method,
                url=build_url(
                    self.BASE_API_URL, url, parameters
                ),
                headers={
                    'Authorization': 'Bearer {}'.format(self._access_token)
                })
            response = await response.json()
        return response

    def refresh_token(self, client_id, client_secret, refresh_token):
        self._access_token, _ = authorization.refresh_access_token(
            client_id, client_secret, refresh_token
        )


class Account(object):
    def __init__(self, id, description, created, client=None, *args, **kwargs):
        self.id = id
        self.description = description
        self.created = dateutil.parser.parse(created)
        self.__client = client

    @property
    def transactions(self):
        return self.list_transactions()

    def __repr__(self):
        return "<Account {} {} ({})>".format(
            self.id, self.description, self.created
        )

    def get_balance(self):
        if self.__client:
            return self.__client.get_balance(account_id=self.id)

    def list_transactions(self, since: datetime.datetime = None,
                          before: datetime.datetime = None,
                          limit: int = None):
        if self.__client:
            return self.__client.list_transactions(
                account_id=self.id, since=since, before=before, limit=limit)

    def list_webhooks(self):
        if self.__client:
            return self.__client.list_webhooks(account_id=self)

    def register_webhook(self, url: str):
        if self.__client:
            return self.__client.register_webhook(url)


class Balance(object):
    def __init__(self, balance, spend_today, currency, generated_at, *args,
                 **kwargs):
        self.amount = Amount(D(balance) / 100, currency)  # it's in pence
        self.spent_today = Amount(D(spend_today) / 100, currency)
        self.currency = currency
        self.generated_at = generated_at

    def __repr__(self):
        return "{} (at {})".format(
            self.amount, self.generated_at)


class Amount(object):
    def __init__(self, value, currency, *args, **kwargs):
        self._value = D(value)
        self._currency = currency

    def __add__(self, other):
        assert self.currency == other.currency, Exception(
            'Different currencies')
        return Amount(self.value + other.value, self.currency)

    def __eq__(self, other):
        return self.value == other.value and self.currency == other.currency

    @property
    def value(self):
        return self._value

    @property
    def currency(self):
        return self._currency

    def __repr__(self):
        return "{:.2f} {}".format(
            self.value, self.currency
        )


class Transaction(object):
    def __init__(self, id, description, amount, currency, created,
                 account_balance, metadata, is_load, settled,
                 local_amount, local_currency, category, attachments,
                 merchant=None, decline_reason=None, client=None,
                 *args, **kwargs):
        self.__client = client
        self.id = id
        self.description = description
        self._amount = Amount(D(amount) / 100, currency)
        self.currency = currency
        self.created = dateutil.parser.parse(created)

        self.attachments = [
            Attachment(**attachment, client=client)
            for attachment in attachments
            ] if attachments else None

        self.merchant = Merchant(**merchant) if isinstance(merchant, dict) else None

        # mondo is UK only for the moment,
        # so you can only have a GBP account currency
        self._account_balance = Amount(D(account_balance) / 100, 'GBP')
        self._local_amount = Amount(D(local_amount / 100), local_currency)
        self.metadata = metadata
        self.is_load = is_load
        self.settled = settled
        self.category = category
        self.decline_reason = decline_reason
        self.emoji = getattr(self.merchant, 'emoji', None)

    @property
    def amount(self):
        return self._amount

    @property
    def account_balance(self):
        return self._account_balance

    @property
    def local_amount(self):
        return self._local_amount

    @property
    def notes(self):
        return self.metadata.get('notes')

    @notes.setter
    def notes(self, value):
        self.add_metadata({'notes': value})

    def add_metadata(self, metadata: dict):
        if self.__client:
            return self.__client.annotate_transaction(self.id, metadata)

    def register_attachment(self, file_url: str, file_type: str):
        if self.__client:
            return self.__client.register_attachment(
                self.id, file_url, file_type
            )

    def __repr__(self):
        return "<Transaction {date:%Y-%m-%d %H:%M} {id} {description} {amount}>".format(
            date=self.created, id=self.id, description=self.description,
            amount=self.amount)


class Merchant(object):
    def __init__(self, id, group_id, name, address, category, logo, emoji,
                 created, metadata, *args, **kwargs):
        self.id = id
        self.group_id = group_id
        self.name = name
        self.address = address
        self.category = category
        self.logo = logo
        self.emoji = emoji
        self.created = created
        self.metadata = metadata

    def __repr__(self):
        return "<Merchant {} ({})>".format(
            self.name, self.category
        )


class Attachment(object):
    def __init__(self, id, user_id, external_id, file_url, file_type, created,
                 client=None, *args, **kwargs):
        self.id = id
        self.user_id = user_id
        self.external_id = external_id
        self.file_url = file_url
        self.file_type = file_type
        self.created = dateutil.parser.parse(created)
        self.__client = client

    def __repr__(self):
        return "<Attachment: {} {} ({}) / {}>".format(
            self.id, self.file_url, self.file_type, self.created
        )

    def deregister(self):
        if self.__client:
            self.__client.deregister_attachment(self.id)


class Webhook(object):
    def __init__(self, id: str, account_id: str, url: str, client=None,
                 *args, **kwargs):
        self.id = id
        self.account_id = account_id
        self.url = url
        self.client = client
        self.active = True

    def delete(self):
        if self.client:
            self.client.delete(self.id)
            self.active = False
            self.url = None

    def __repr__(self):
        return "<Webhook {} {}>".format(
            self.id, self.url
        )
