from decimal import Decimal as D

import dateutil.parser
import requests

from mondo.utils import build_url


class MondoApiException(Exception):
    pass


class MondoEntity(object):
    @classmethod
    def from_response(cls, class_name: str, json: dict, *args, **kwargs):
        """
        Build the appropriate object from a response
        :param response:
        :param class_name:
        :return:
        """
        cls._response = json
        subclasses = {klass.__name__: klass for klass in MondoEntity.__subclasses__()}
        return subclasses[class_name](*args, **cls._response, **kwargs)

    def json(self):
        return self._response


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

    ENTITIES_TO_ENTITY = {
        'accounts': 'Account',
        'transactions': 'Transaction',
        'attachments': 'Attachment',
        'webhooks': 'Webhook',
    }  # TODO: Refactor

    ENTITY_TO_ENTITIES = {
        'Account': 'accounts',
        'Transaction': 'transactions',
        'Attachment': 'attachments',
        'Webhook': 'webhooks'
    }  # TODO: Refactor

    def _list_of(self, entities_name: str, **kwargs):
        response = self._make_request(
            '/{}'.format(entities_name.lower()), kwargs
        )
        if response.ok:
            entity_name = self.ENTITIES_TO_ENTITY[entities_name]
            return [
                MondoEntity.from_response(entity_name, entity)
                for entity in response.json()[entities_name]
            ]
        else:
            raise MondoApiException(response.json()['message'])

    def _get(self, entity_name: str, entity_id: str, **kwargs):
        entities_name = self.ENTITY_TO_ENTITIES[entity_name.capitalize()]
        response = self._make_request(
            '/{}/{}'.format(
                entities_name, entity_id
            ), kwargs
        )

        if response.ok:
            return MondoEntity.from_response(
                entity_name.capitalize(), response.json()[entity_name.lower()]
            )
        else:
            raise MondoApiException(response.json()['message'])

    def _create(self):
        pass

    def _delete(self):
        pass


class Transaction(MondoEntity):
    def __init__(self, id, description, amount, currency, created, merchant,
                 account_balance, metadata, notes, is_load, settled, category,
                 decline_reason=None, *args, **kwargs):
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

    @property
    def amount(self):
        return Amount(self._amount, self.currency)

    def __repr__(self):
        return "<Transaction {} {}>".format(
            self.id, self.description, self.amount
        )


class Merchant(MondoEntity):
    def __init__(self, id, group_id, name, address, category, logo, emoji, created,
                 metadata, *args, **kwargs):
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


class Account(MondoEntity):
    def __init__(self, id, description, created):
        self.id = id
        self.description = description
        self.created = dateutil.parser.parse(created)

    def __repr__(self):
        return "<Account {} {} ({})>".format(
            self.id, self.description, self.created
        )


class Balance(MondoEntity):
    def __init__(self, balance, spend_today, currency, generated_at):
        self.balance = Amount(balance, currency)  # it's in pence
        self.spent_today = Amount(spend_today, currency)
        self.generated_at = generated_at

    def __repr__(self):
        return "{} (at {})".format(
            self.balance, self.generated_at)


class Attachment(MondoEntity):
    def __init__(self, id, user_id, external_id, file_url, file_type, created, *args, **kwargs):
        self.id = id
        self.user_id = user_id
        self.external_id = external_id
        self.file_url = file_url
        self.file_type = file_type
        self.created = dateutil.parser.parse(created)

    def __repr__(self):
        return "<Attachment: {} {} ({}) / {}>".format(
            self.id, self.file_url, self.file_type, self.created
        )


class Webhook(MondoEntity):
    def __init__(self, id: str, account_id: str, url: str, *args, **kwargs):
        self.id = id
        self.account_id = account_id
        self.url = url

    def __repr__(self):
        return "<Webhook {} {}>".format(
            self.id, self.url
        )


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
