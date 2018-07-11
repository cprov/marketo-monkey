# marketo-monkey [![Snap Status](https://build.snapcraft.io/badge/cprov/marketo-monkey.svg)](https://build.snapcraft.io/user/cprov/marketo-monkey)

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
$ marketo-monkey.py set_lead
'Lead' object available fields:
    email, firstName, hasSnapInEdge, hasSnapInStable, hasSnapRevision, hasStrictSnap, lastName, snapInEdgeDate, snapInStableDate, snapNameEdge, snapNameRegisteredDate, snapNameStable, snapNameUploaded, snapRevisionUploadedDate, snapStoreAccountID, snapStoreID, snapcraft, snapcraftio, snapcraftioEnvironment, snapname, userDisplayName

$ marketo-monkey.py set_lead email=foo.bar@example.com
Lead object 33374563 updated!
{'email': 'foo.bar@example.com',
 'firstName': 'Foo',
 'hasSnapInEdge': False,
 'hasSnapInStable': False,
 'hasSnapRevision': False,
 'hasStrictSnap': False,
 'id': 33374563,
 'lastName': 'Bar',
 'snapInEdgeDate': None,
 'snapInStableDate': None,
 'snapNameEdge': None,
 'snapNameRegisteredDate': None,
 'snapNameStable': None,
 'snapNameUploaded': None,
 'snapRevisionUploadedDate': None,
 'snapStoreAccountID': '1964',
 'snapStoreID': '1234',
 'snapcraft': False,
 'snapcraftio': True,
 'snapcraftioEnvironment': 'staging',
 'snapname': None,
 'userDisplayName': None}

$ marketo-monkey set_snap
'Snap' object available fields:
    channel, confinement, revision, snapName, snapStoreAccountID

$ marketo-monkey set_snap snapStoreAccountID=1234,snapNamexx=testing-snap5
Failed to create or modify snap!
    Field 'snapNamexx' not found
    Value for requried field 'snapname' not specified

$ marketo-monkey set_snap snapStoreAccountID=1964,snapName=testing-snap5
Snap object '44f7bc36-71a3-4ed1-9197-a727911dfa8f' created!
{'channel': None,
 'confinement': None,
 'createdAt': '2018-06-21T00:59:50Z',
 'marketoGUID': '44f7bc36-71a3-4ed1-9197-a727911dfa8f',
 'revision': None,
 'seq': 0,
 'snapName': 'testing-snap5',
 'snapStoreAccountID': '1964',
 'updatedAt': '2018-06-21T00:59:50Z'}

$ marketo-monkey get_snaps
'Snap' object searchable fields:
    marketoGUID, snapName, snapStoreAccountID

$ marketo-monkey.py get_snaps snapStoreAccountID=1964
...
{'channel': 'edge',
 'confinement': 'devmode',
 'createdAt': '2018-06-20T19:07:44Z',
 'marketoGUID': '671257db-1462-4b48-84f3-3d57d91fe396',
 'revision': '101',
 'seq': 2,
 'snapName': 'test-snap',
 'snapStoreAccountID': '1964',
 'updatedAt': '2018-06-21T00:02:25Z'}
{'channel': None,
 'confinement': None,
 'createdAt': '2018-06-21T00:59:50Z',
 'marketoGUID': '44f7bc36-71a3-4ed1-9197-a727911dfa8f',
 'revision': None,
 'seq': 3,
 'snapName': 'testing-snap5',
 'snapStoreAccountID': '1964',
 'updatedAt': '2018-06-21T00:59:50Z'}

$ marketo-monkey.py set_repo snapStoreAccountID=1980,snapName=foo-baz,reponame=/foo/baz
...
{'createdAt': '2018-07-11T18:17:50Z',
 'firstSuccessfulBuild': False,
 'marketoGUID': '6f0653b6-1ff3-4b70-a700-b4c9ceb047ab',
 'repoName': '/foo/baz',
 'seq': 0,
 'snapName': 'foo-baz',
 'snapStoreAccountID': '1980',
 'updatedAt': '2018-07-11T18:17:50Z'}

$ marketo-monkey get_repos snapStoreAccountID=1980
...
{'createdAt': '2018-07-11T18:17:50Z',
 'firstSuccessfulBuild': False,
 'marketoGUID': '6f0653b6-1ff3-4b70-a700-b4c9ceb047ab',
 'repoName': '/foo/baz',
 'seq': 2,
 'snapName': 'foo-baz',
 'snapStoreAccountID': '1980',
 'updatedAt': '2018-07-11T18:17:50Z'}


```
