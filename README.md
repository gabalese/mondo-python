# Mondo Python SDK

A simple python SDK to wrap the Mondo API.

See the docs [https://getmondo.co.uk/docs](https://getmondo.co.uk/docs) for details.

## How does the SDK work

### Get an access token

The latest version of the Mondo API effectively makes the user and password
login process deprecated. You're now expected to go through the oauth process
in order to get an access token.

I've included an utility script do help you to do that. Simply run:

`python -m tools.get_access_token`

And follow the steps on screen.

### Refresh an access token

You'll get an access token that expires after a couple of hours.
If you register a confidential app, you'll also be allowed to
refresh your token. I wrote another utility script to do that:

`python -m tools.refresh_access_token`

## What can I do?


### Client

Instantiate a client using the access token:
```
from mondo import MondoClient
client = MondoClient('<your_access_token_here>')
```

The client will allow you to use (almost) every API method:

```
client.whoami()
client.list_accounts()
client.get_balance('<account_id>')
client.list_transactions('<account_id>')
client.get_transaction('<transaction_id')
client.annotate_transaction('<transaction_id>', {'key':'value'})
client.list_webhooks('<account_id>')
client.register_webhook('<account_id>', 'http://my.app.domain/callback')
client.delete_webhook('<webhooh_id>')
client.register_attachment('<transaction_id>', 'http://my.file/url.png', 'image/png')
client.deregister_attachment('<attachment_id')
```

Each method returns a list of relevant entities.
(I.e `list_accounts` will return a `list[Account]`)
Each entity exposes helper methods.


### Account

You can get the default account by:

`client.list_accounts()[0]`

An `Account` supports the following methods:
```python
account.get_balance()
account.list_transactions()
account.list_webhooks()
account.register_webhook('<url>')
```

### Balance

A `Balance` supports the following properties:
```
balance.amount
balance.spent_today
balance.generated_at

```

#### Amount

```
amount.value
amount.currency
```


### Transaction

A `Transaction` supports the following properties:

```python
transaction.amount
transaction.metadata
transaction.created
```

... and the following methods:

```python
transaction.annotate({'key': 'value'})
transaction.register_attachment('<file_url>', '<file_type>')
```


### Attachment

```python
attachment.deregister()
```

### Webhook

```python
webhook.delete()
```

# Contribute

[See the docs for a detailed explanation](https://getmondo.co.uk/docs) and details.

I tried to keep the code readable and detailed, even little bit verbose perhaps.
There are no tests at the moment, since I felt too lazy to mock the whole API
and wanted to play with my transaction feed ASAP.

Feel free to add them, possibly in `py.test` style.


# Credits

Forked from [simonvc/mondo-python](https://github.com/simonvc/mondo-python), which in
turn was forked from [titomiguelcosta/mondo](https://bitbucket.org/titomiguelcosta/mondo).
