# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pip install -r requirements-vendor.txt -t lib/
# [START vendor]
from google.appengine.ext import vendor
vendor.add('lib')
# [END vendor]

# monkey-patch for ImportError: No module named pwd
# ref: https://github.com/GoogleCloudPlatform/google-cloud-python/issues/2032
# import os.path
# def patched_expanduser(path):
#     return path
# os.path.expanduser = patched_expanduser
