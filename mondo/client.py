import datetime

from mondo.authorization import MongoAuthException
from mondo.mondo import (Account, Balance, MondoApiException, Transaction,
                         Attachment, Webhook, MondoApi)


class MondoClient(MondoApi):
    def whoami(self):
        """
        Check the access token for validity

        :return: response as json
        """
        response = self._make_request('/ping/whoami')
        if response.ok:
            return response.json()
        else:
            raise MondoApiException(response.json()['message'])

    def list_accounts(self):
        """
        List the accounts linked to the user.
        (Mondo only allows one for the moment)

        :return: an Account object
        """
        response = self._make_request('/accounts')

        if response.ok:
            return [
                Account(**account)
                for account in response.json()['accounts']
                ]
        else:
            raise MongoAuthException(response.json()['message'])

    def get_balance(self, account_id: str):
        """
        Get the current balance for the account

        :param account_id:
        :return: a Balance object
        """
        response = self._make_request('/balance', {'account_id': account_id})

        if response.ok:
            return Balance(
                **response.json(),
                generated_at=datetime.datetime.now())
        else:
            raise MondoApiException(response.json()['message'])

    def list_transactions(self, account_id: str, since: str = None,
                          before=None, limit=None):
        """
        List recent transactions for the account

        :param account_id: account id
        :param before: only list transactions before that date (as RFC formatted)
        :param since: only list transactions after that date (as RFC formatted)
        :param limit: only show a number of transactions
        :return: A list of Transaction objects
        """

        params = {
            'account_id': account_id,
            'expand[]': 'merchant'
        }
        if since:
            params.update({'since': since})
        if before:
            params.update({'before': before})
        if limit:
            params.update({'limit': limit})

        response = self._make_request('/transactions', params)

        if response.ok:
            return [
                Transaction(**transaction)
                for transaction in response.json()['transactions']
            ]
        else:
            raise MondoApiException(response.json()['message'])

    def get_transaction(self, transaction_id: str):
        """
        Get details on a specific transaction

        :param transaction_id: Transaction.id as returned by a list
        :return: a Transaction
        """
        response = self._make_request(
            '/transactions/{}'.format(transaction_id),
            {'expand[]': 'merchant'}
        )

        if response.ok:
            return Transaction(**response.json()['transaction'])
        else:
            raise MondoApiException(response.json()['message'])

    def annotate_transaction(self, transaction_id: str, metadata: dict):
        """
        Add metadata to a transaction.
        To delete metadata keys, update the key with an empty value

        :param transaction_id:
        :param metadata: a dictionary of metadata
        :return: a Transaction object
        """
        metadata = {'metadata[{}]'.format(key): value
                    for key, value in metadata.items()}

        response = self._make_request(
            '/transactions/{}'.format(transaction_id),
            method='PATCH',
            data=metadata
        )

        if response.ok:
            return Transaction(**response.json())
        else:
            raise MondoApiException(response.json()['message'])

    def create_feed_item(self, account_id, feed_item):
        """
        # TODO

        :param account_id:
        :param feed_item:
        :return:
        """
        raise NotImplementedError

    def list_webhooks(self, account_id: str):
        """
        List webhooks currently associated to the account

        :param account_id: account id
        :return: a json list of webhooks (might be objects? TODO)
        """
        response = self._make_request(
            url='/webhooks',
            parameters={
                'account_id': account_id
            }
        )

        if response.ok:
            return [
                Webhook(**webhook)
                for webhook in response.json()['webhooks']
            ]
        else:
            raise MondoApiException(response.json()['message'])

    def register_webhook(self, account_id: str, url: str):
        """
        Register a url to handle transaction events
        (Docs say that only transaction events are sent at this time)

        :param account_id:
        :param url: The wbhook url where the events will be forwarded
        :return: a json representation of a webook
        """
        response = self._make_request(
            method='POST',
            url='/webhooks',
            data={
                'account_id': account_id,
                'url': url
            }
        )

        if response.ok:
            return Webhook(**response.json()['webook'])
        else:
            raise MondoApiException(response.json()['message'])

    def delete_webook(self, webhook_id: str):
        """
        Delete a webhook

        :param webhook_id: the id of a webhook to delete
        :return: An empty dict
        """
        response = self._make_request(
            method='DELETE',
            url='/webhooks/{}'.format(webhook_id)
        )
        if response.ok:
            return {}
        else:
            raise MondoApiException(response.json()['message'])

    def register_attachment(self, transaction_id: str, file_url: str,
                            file_type: str):
        """
        Register an attachment url against a transaction

        :param transaction_id: the transaction id to add an attachment to
        :param file_url: the attachment url
        :param file_type: the (MIME) file type (es. 'image/png')
        :return: an Attachment object
        """
        response = self._make_request(
            method='POST',
            url='/attachment/register',
            data={
                'external_id': transaction_id,
                'file_type': file_type,
                'file_url': file_url
            }
        )

        if response.ok:
            return Attachment(**response.json()['attachment'])
        else:
            raise MondoApiException(response.json()['message'])

    def deregister_attachment(self, attachment_id):
        """
        Delete an attachment

        :param attachment_id: the Attachment id
        :return: an empty dict
        """
        response = self._make_request(
            method='POST',
            url='/attachment/deregister',
            data={
                'id': attachment_id
            }
        )

        if response.ok:
            return {}
        else:
            raise MondoApiException(response.json()['message'])
