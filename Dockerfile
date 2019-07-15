# Copyright (c) 2017 5GTANGO
# ALL RIGHTS RESERVED.
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
#
# Neither the name of the SONATA-NFV, 5GTANGO
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
#
# This work has been performed in the framework of the 5GTANGO project,
# funded by the European Commission under Grant number 761493 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the 5GTANGO
# partner consortium (www.5gtango.eu).

FROM python:3.4-slim
MAINTAINER 5GTANGO

RUN apt-get update && apt-get install -y gcc && apt-get install -y git
RUN apt-get install -y git
RUN pip install git+git://github.com/eandersson/amqpstorm.git@feature/reuse_channels

# Configuration
ENV broker_host amqp://guest:guest@localhost:5672/%2F
ENV broker_exchange son-kernel

# ENV Postgres
ENV POSTGRES_USER sonata
ENV POSTGRES_PASSWORD sonatatest
ENV DATABASE_HOST son-postgres
ENV DATABASE_PORT 5432

# add src files
WORKDIR /
ADD setup.py /tng-ia-emu/
ADD requirements.txt /tng-ia-emu/
ADD src/emulator_wrapper /tng-ia-emu/src/emulator_wrapper

# install wrapper
WORKDIR /tng-ia-emu
RUN python setup.py develop

CMD ["tng-ia-emu"]

