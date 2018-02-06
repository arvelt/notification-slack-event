#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://www.googleapis.com/storage/v1/b/appengine-sdks/o?prefix=featured
# Thanks to https://github.com/yosukesuzuki/goisky-tools/blob/master/ciscripts/getlatestsdk.py

import os
import json
import re
from urllib2 import urlopen, URLError, HTTPError

SDK_URL = 'https://www.googleapis.com/storage/v1/b/appengine-sdks/o?prefix=featured/google_appengine'


def get_latest_sdk_url():
    f = urlopen(SDK_URL)
    sdks = json.loads(f.read())

    try:
        for item in reversed(sdks['items']):
            if item['metageneration'] == '2':
                url = item['mediaLink']
                break
    except KeyError as e:
        print "KeyError %s", e
    return url


def dlfile(url):
    # Open the url
    try:
        f = urlopen(url)
        print "downloading " + url

        # Open our local file for writing
        with open("python_appengine_sdk-latest.zip", "wb") as local_file:
            local_file.write(f.read())
        local_file.close()

    # handle errors
    except HTTPError as e:
        print "HTTP Error:", e.code, url
    except URLError as e:
        print "URL Error:", e.reason, url


def main():
    url = get_latest_sdk_url()
    print url
    dlfile(url)

if __name__ == '__main__':
    main()
