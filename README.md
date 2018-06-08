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


    $ marketo-monkey -v
    2018-06-08 14:21:10,846 DEBUG Added a stderr logging handler to logger: urllib3
    Starting new HTTPS connection (1): <REDACTED>.mktorest.com
    https://<REDACTED>.mktorest.com:443 "GET /identity/oauth/token?client_id=<REDACTED>&grant_type=client_credentials&client_secret=<REDACTED> HTTP/1.1" 200 None
    Starting new HTTPS connection (1): <REDACTED>.mktorest.com
    https://<REDACTED>.mktorest.com:443 "GET /rest/v1/customobjects/snap_c/describe.json?access_token=<REDACTED> HTTP/1.1" 200 None
    {'requestId': '1477e#163dfc5d0b6',
     'result': [{'createdAt': '2018-06-06T13:24:08Z',
    ...
