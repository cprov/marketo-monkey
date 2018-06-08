# marketo-monkey

CLI tool to facilitate Marketo integration.

## Installing

Use `snap`:

    $ snap install marketo-monkey [--edge] [--classic]

`--classic` would allow you to edit the configuration file
(credentials) from the tool, otherwise it's not necessary.

    $ marketo-monkey -v
    2018-06-08 14:26:12,793 DEBUG Added a stderr logging handler to logger: urllib3
    Could not access the configuration file ...
    Please edit /home/ubuntu/snap/marketo-monkey/common/marketo-monkey.yaml manually


## Usage

```
$ marketo-monkey lead
'Lead' object available fields:
    firstName, lastName, email, company

$ marketo-monkey lead email=foo.bar@example.com
Lead object updated!
{'createdAt': '2018-06-08T12:19:00Z',
 'email': 'foo.bar@example.com',
 'firstName': 'Foo',
 'id': 33374563,
 'lastName': 'Bar',
 'updatedAt': '2018-06-08T17:57:07Z'}

$ marketo-monkey snap
'Snap' object available fields:
    createdAt, marketoGUID, updatedAt, Confinement, channel, emailAddress, revision, snapName

$ marketo-monkey snap emailAddress=foo.bar@example.com,snapNamexx=testing-snap5
Failed to create or modify snap!
    Field 'snapNamexx' not found
    Value for requried field 'snapname' not specified

$ marketo-monkey snap emailAddress=foo.bar@example.com,snapName=testing-snap5
Snap object created!
{'Confinement': None,
 'channel': None,
 'createdAt': '2018-06-08T18:34:21Z',
 'emailAddress': 'foo.bar@example.com',
 'marketoGUID': 'e1361ee9-7f9e-4a2c-acb4-b7e988ac8c55',
 'revision': None,
 'seq': 0,
 'snapName': 'testing-snap5',
 'updatedAt': '2018-06-08T18:34:21Z'}
```
