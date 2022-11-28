# Sample Lustre Jobstats

This repository holds sample programs that allow lustre jobs stats to be accessed
from a remote machine as json data. The software that is installed on the lustre
server is minimal and only relies on python packages already installed by DDN.
This allows the data to be processed on a more general-purpose machine which may
have arbitrary software installed and be bound to directory services for lookups.

This repository provides the software discussed at the UK lustre user group
meeting on the 30th of November 2022 in Manchester

## Getting started

Once the web server is running on the lustre servers and the cron
job is injecting data into grafana then graphs like these are available.

![plot](./media/example\ lustre\ stats.png)

There are further readme's in the directories for the lustre servers
and the monitoring host.

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
