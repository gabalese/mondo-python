from typing import List
import datetime

from mondo.mondo import MondoApi, Account, Balance, Transaction, Attachment, Webhook


class MondoClient(MondoApi):
    def whoami(self):
        """
        Check the access token for validity

        :return: response as json
        """
        return self._make_request('/ping/whoami')

    def list_accounts(self) -> List[Account]:
        """
        List the accounts linked to the user.
        (Mondo only allows one for the moment)

        :return: an Account object
        """
        response = self._make_request('/accounts')

        return [
            Account(client=self, **account) for account in response['accounts']
        ]

    def get_balance(self, account_id: str) -> Balance:
        """
        Get the current balance for the account

        :param account_id:
        :return: a Balance object
        """
        response = self._make_request('/balance', {'account_id': account_id})

        return Balance(generated_at=datetime.datetime.now(), **response)

    def list_transactions(self, account_id: str, since: str = None,
                          before=None, limit=None) -> List[Transaction]:
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

        return [
            Transaction(client=self, **transaction)
            for transaction in response['transactions']
        ]

    def get_transaction(self, transaction_id: str) -> Transaction:
        """
        Get details on a specific transaction

        :param transaction_id: Transaction.id as returned by a list
        :return: a Transaction
        """
        response = self._make_request(
            '/transactions/{}'.format(transaction_id),
            {'expand[]': 'merchant'}
        )

        return Transaction(client=self, **response['transaction'])

    def annotate_transaction(self, transaction_id: str, metadata: dict) -> Transaction:
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

        return Transaction(client=self, **response['transaction'])

    def create_feed_item(self, account_id, feed_item):
        """
        # TODO

        :param account_id:
        :param feed_item:
        :return:
        """
        raise NotImplementedError

    def list_webhooks(self, account_id: str) -> List[Webhook]:
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

        return [
            Webhook(client=self, **webhook) for webhook in response['webhooks']
        ]

    def register_webhook(self, account_id: str, url: str) -> Webhook:
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

        return Webhook(client=self, **response['webook'])

    def delete_webook(self, webhook_id: str) -> dict:
        """
        Delete a webhook

        :param webhook_id: the id of a webhook to delete
        :return: An empty dict
        """
        self._make_request(
            method='DELETE',
            url='/webhooks/{}'.format(webhook_id)
        )
        return {}

    def register_attachment(self, transaction_id: str, file_url: str,
                            file_type: str) -> Attachment:
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

        return Attachment(client=self, **response['attachment'])

    def deregister_attachment(self, attachment_id) -> dict:
        """
        Delete an attachment

        :param attachment_id: the Attachment id
        :return: an empty dict
        """
        self._make_request(
            method='POST',
            url='/attachment/deregister',
            data={
                'id': attachment_id
            }
        )

        return {}
