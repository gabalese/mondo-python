# Mondo simple python SDK

A simple python SDK for dealing with the Mondo API.

See the docs https://getmondo.co.uk/docs for details.

## How do I load the SDK

### Get an access token

The latest version of the Mondo API effectively makes the user and password
login process deprecated. You're now expected to go through the oauth process
in order to get an access token.

I've included an utility script do help you do that:

`python -m tools.get_access_token`

And follow the steps on screen.

### Refresh an access token

You'll get an access token that expires after a couple of hours.
If you register a confidential app, you'll be allowed to
refresh your token. I wrote another utility script to do just that.

`python -m tools.refresh_access_token`

## What can you do?

Instantiate a client using the access token:
```
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
I'm still missing the implementation of a `create_feed_item`. So that's the first #TODO

[See the docs for a detailed explanation](https://getmondo.co.uk/docs) and details.

# Contribute


I tried to keep the code readable and detailed, even little bit verbose perhaps.
There are no tests at the moment, since I felt too lazy to mock the whole API
and wanted to play with my transaction feed ASAP.

Feel free to add them, possibly in `py.test` style.


# Credits

Forked from [simonvc/mondo-python](https://github.com/simonvc/mondo-python), which in
turn was forked from [titomiguelcosta/mondo](https://bitbucket.org/titomiguelcosta/mondo).
