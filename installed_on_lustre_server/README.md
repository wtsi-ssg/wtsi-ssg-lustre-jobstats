# Lustre job stats exporter


This directory holds two sample web apps that export job stats
information from a lustre file system via an api endpoint

```
curl -s  http://lus23-oss1-mgmt.internal.sanger.ac.uk:8081  | jq .
{
  "lus23-OST0001": [
    {
      "write_bytes": {
        "max": 16777216,
        "sum": 1275960319678,
        "samples": 413177,
        "unit": "bytes",
        "min": 4
      },
      "job_id": "SA1TwDkwOzA7,team135",
      "setattr": {
        "samples": 7,
        "unit": "reqs"
      },
….
      "read_bytes": {
        "max": 16777216,
        "sum": 51588627873792,
        "samples": 22190157,
        "unit": "bytes",
        "min": 4096
      },
      "snapshot_time": 1667913397
    }
  ]
}
```

The imported python libraries are installed by default on an
exascaler system. We have included a sample systemd service
file `lustre-stats-web.service` which can be used to ensure that
the web service is started on boot.

The two versions of the code show a generic stats server and
one where the data is enriched from the decoded job name.

## Authors and acknowledgment
James Beal & Dave Holland 

## License
Copyright (c) 2022 Genome Research Ltd. 

Author: James Beal <James.Beal@sanger.ac.uk> , Dave Holland <dh3@sanger.ac.uk>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
