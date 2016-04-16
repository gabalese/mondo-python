from decimal import Decimal as D

from unittest import mock
from mondo.client import MondoApi, MondoClient
from mondo.mondo import Amount
from test import mock_api_response as responses


@mock.patch.object(MondoApi, '_make_request')
def test_client_list_accounts(mock_request):
    mock_request.return_value = responses.LIST_ACCOUNTS

    client = MondoClient('randomToken')
    accounts = client.list_accounts()

    assert len(accounts) == 1
    assert accounts[0].id == 'my_awesome_account_id'
    assert accounts[0].description == 'Gabriele Alese'


@mock.patch.object(MondoApi, '_make_request')
def test_client_list_transactions(mock_request):
    mock_request.side_effect = [
        responses.LIST_ACCOUNTS, responses.LIST_TRANSACTIONS
    ]

    client = MondoClient('randomToken')
    acc = client.list_accounts()[0]
    transactions = acc.list_transactions()

    assert len(transactions) == 3

    top_up = transactions[0]

    assert top_up.amount.value == D('100.00')
    assert top_up.category == 'mondo'

    cigarettes = transactions[1]
    assert cigarettes.merchant.name == 'The Co-operative Food'
    assert cigarettes.merchant.metadata['foursquare_category'] == 'Grocery Store'

    lunch = transactions[2]

    assert lunch.amount == Amount('-5.50', 'GBP')
    assert lunch.local_amount == Amount('-5.50', 'GBP')
    assert lunch.account_balance == Amount('88', 'GBP')

    assert sum([transaction.amount.value for transaction in transactions]) == D('88')


@mock.patch.object(MondoApi, '_make_request')
def test_client_balance(mock_request):
    mock_request.return_value = responses.BALANCE

    client = MondoClient('randomToken')
    balance = client.get_balance('my_awesome_account_id')

    assert balance.amount == Amount('19.51', 'GBP')
    assert balance.currency == 'GBP'
