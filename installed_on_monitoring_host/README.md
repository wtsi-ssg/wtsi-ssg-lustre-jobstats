# Lustre job stats injector

This directory holds the job which fetches stats from each of the 
lustre servers and processes it and then sends the processed data
on to grafana.

We have a cronjob on a monitoring node that collects data every 
three minutes.

```
root@lus-mon01:~# crontab -l | grep jobst
*/3 * * * * /software/isg/scripts/jobsstats -l lus20 -s lus20-mds1-mgmt -s lus20-mds2-mgmt -s lus20-oss1-mgmt -s lus20-oss2-mgmt -s lus20-oss3-mgmt -s lus20-oss4-mgmt -s lus20-oss5-mgmt -s lus20-oss6-mgmt | logger -t jobstats
*/3 * * * * /software/isg/scripts/jobsstats -l lus23 -s lus23-mds1-mgmt -s lus23-mds2-mgmt -s lus23-oss1-mgmt -s lus23-oss2-mgmt -s lus23-oss3-mgmt -s lus23-oss4-mgmt -s lus23-oss5-mgmt -s lus23-oss6-mgmt | logger -t jobstats
*/3 * * * * /software/isg/scripts/jobsstats -l lus24 -s lus24-mds1-mgmt -s lus24-mds2-mgmt  -s lus24-mds3-mgmt -s lus24-mds4-mgmt -s lus24-oss1-mgmt -s lus24-oss2-mgmt -s lus24-oss3-mgmt -s lus24-oss4-mgmt -s lus24-oss5-mgmt -s lus24-oss6-mgmt | logger -t jobstats
*/3 * * * * /software/isg/scripts/jobsstats -l lus25 -s lus25-mds1-mgmt -s lus25-mds2-mgmt  -s lus25-mds3-mgmt -s lus25-mds4-mgmt -s lus25-oss1-mgmt -s lus25-oss2-mgmt -s lus25-oss3-mgmt -s lus25-oss4-mgmt -s lus25-oss5-mgmt -s lus25-oss6-mgmt | logger -t jobstats
*/3 * * * * /software/isg/scripts/jobsstats -l lus26 -s lus26-mds1-mgmt -s lus26-mds2-mgmt  -s lus26-mds3-mgmt -s lus26-mds4-mgmt -s lus26-oss1-mgmt -s lus26-oss2-mgmt -s lus26-oss3-mgmt -s lus26-oss4-mgmt -s lus26-oss5-mgmt -s lus26-oss6-mgmt | logger -t jobstats
```

We have one cronjob per filesystem, the label for the filesystem
is passed with -l and a -s servername argument is given once 
per lustre server. As the stats server lists the mounted
OST's and MDT's every get this means the stats are resilient 
in the face of failover.

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
