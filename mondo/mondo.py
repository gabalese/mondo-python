from decimal import Decimal as D

import dateutil.parser
import requests

from mondo import authorization
from mondo.utils import build_url


class MondoApiException(Exception):
    pass


class MondoApi(object):
    BASE_API_URL = 'https://api.getmondo.co.uk'

    def __init__(self, access_token: str):
        """
        :param access_token: The access token, as returned by the OAuth dance
        """
        self.__access_token = access_token

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
                'Authorization': 'Bearer {}'.format(self.__access_token)
            }, **kwargs
        )
        return response

    def refresh_token(self, client_id, client_secret, refresh_token):
        self.__access_token, _ = authorization.refresh_access_token(
            client_id, client_secret, refresh_token
        )


class Account(object):
    def __init__(self, id, description, created, client=None):
        self.id = id
        self.description = description
        self.created = dateutil.parser.parse(created)
        self.client = client

    def __repr__(self):
        return "<Account {} {} ({})>".format(
            self.id, self.description, self.created
        )

    def get_balance(self):
        if self.client:
            return self.client.get_balance(account_id=self.id)

    def list_transactions(self):
        if self.client:
            return self.client.list_transactions(account_id=self.id)

    def list_webhooks(self):
        if self.client:
            return self.client.list_webhooks(account_id=self)

    def register_webhook(self, url: str):
        if self.client:
            return self.client.register_webhook(url)


class Balance(object):
    def __init__(self, amount, spend_today, currency, generated_at):
        self.amount = Amount(amount, currency)  # it's in pence
        self.spent_today = Amount(spend_today, currency)
        self.generated_at = generated_at

    def __repr__(self):
        return "{} (at {})".format(
            self.amount, self.generated_at)


class Amount(object):
    def __init__(self, value, currency):
        self._value = D(value)
        self._currency = currency

    def __eq__(self, other):
        return self.value == other.value and self.currency == self.currency

    @property
    def value(self):
        return self._value

    @property
    def currency(self):
        return self._currency

    def __repr__(self):
        return "{:.2f} {}".format(
            self.value / 100, self.currency
        )


class Transaction(object):
    def __init__(self, id, description, amount, currency, created, merchant,
                 account_balance, metadata, notes, is_load, settled,
                 category, decline_reason=None, client=None,
                 *args, **kwargs):

        self.id = id
        self.description = description
        self._amount = amount
        self.currency = currency
        self.created = dateutil.parser.parse(created)
        self.merchant = None
        if merchant:
            self.merchant = Merchant(**merchant)
        self._account_balance = account_balance
        self.metadata = metadata
        self.notes = notes
        self.is_load = is_load
        self.settled = settled
        self.category = category
        self.decline_reason = decline_reason
        self.client = client

    @property
    def amount(self):
        return Amount(self._amount, self.currency)

    def annotate(self, metadata: dict):
        if self.client:
            return self.client.annotate_transaction(self.id, metadata)

    def register_attachment(self, file_url: str, file_type: str):
        if self.client:
            return self.client.register_attachment(
                self.id, file_url, file_type
            )

    def __repr__(self):
        return "<Transaction {} {}>".format(
            self.id, self.description, self.amount
        )


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
        self.client = client

    def __repr__(self):
        return "<Attachment: {} {} ({}) / {}>".format(
            self.id, self.file_url, self.file_type, self.created
        )

    def deregister(self):
        if self.client:
            self.client.deregister_attachment(self.id)


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