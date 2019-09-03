[![Build Status](https://jenkins.sonata-nfv.eu/buildStatus/icon?job=tng-sp-ia-emu/master)](https://jenkins.sonata-nfv.eu/job/tng-sp-ia-emu/job/master/)
[![Join the chat at https://gitter.im/sonata-nfv/5gtango-sp](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/5gtango-sp)
 
 <p align="center"><img src="https://github.com/sonata-nfv/tng-api-gtw/wiki/images/sonata-5gtango-logo-500px.png" /></p>

# tng-sp-ia-emu

The `tng-sp-ia-emu` component is part of [**SONATA's (powered by 5GTANGO)**](https://5gtango.eu/) service platform. It serves as a wrapper around the [Emulator](https://github.com/sonata-nfv/son-emu) VIM and WIM, to manage the interface between the MANO Framework and the Emulator, so that the MANO Framework can orchestrate on the emulated comnpute and networking resources.

## Installation and Dependencies

`tng-sp-ia-emu` is developed in python3, and can be locally installed with

```bash
git clone https://github.com/sonata-nfv/tng-sp-ia-emu.git
cd tng-sp-ia-emu
python3 setup.py install
```
To install it in a Docker container, run

```bash
docker build -t <image_name> -f Dockerfile .
```
Or pull the latest stable version by

```bash
docker pull tsoenen/sonmano-emuwrapper
```

To install, download or use the component as a Docker container, Docker needs to be installed. The depedencies of the component itself are listed in `requirements.txt`.

## Usage

The component requires the following ENV variables:

```yaml
broker_host: <url to the RabbitMQ message broker>
broker_exchange: <exchange on the RabbitMQ message broker>
topic_prefix: <wrapper_name_prefix>
path_to_nbi: <url of the IA NBI>, only when used as part of the 5GTANGO SP
emulator_path: <url of REST API of Emulator that should be orchestrated>
```

The northbound API of the component is described [here](https://github.com/sonata-nfv/tng-sp-ia/wiki/IA-RabbitMQ-Internal-Interface), and is consumed through a RabbitMQ Message broker of which the connection details are passed as ENV variables.
The `{wrapper_name}` is being substituted by the ENV `topic_prefix`. The component requires the Emulator to be running, and its REST API should also be available through an ENV.

If correctly installed, the component can be executed using 

```bash
tng-ia-emu
```

or

```bash
docker run <container_name> <env variables>
```
To install the component as part of a 5GTANGO SP, follow the instructions on [tng-devops](https://github.com/sonata-nfv/tng-devops). When running the ansible-playbook, add an extra `-e "component=emulator"` to the CLI command.

To use the Emulator and this emulator wrapper locally with a standalone MANO Framework, follow the installation instructions on [son-mano-framework](https://github.com/sonata-nfv/son-mano-framework#installation-and-usage).

## Development

To contribute to the development of this 5GTANGO component, you may use the very same development workflow as for any other 5GTANGO Github project. That is, you have to fork the repository and create pull requests.

## License

This 5GTANGO component is published under Apache 2.0 license. Please see the LICENSE file for more details.

#### Lead Developers

The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

- Thomas Soenen ([@tsoenen](https://github.com/tsoenen))

#### Feedback-Channel

* Mailing list [sonata-dev-list](mailto:sonata-dev@lists.atosresearch.eu)
* Gitter room [![Gitter](https://badges.gitter.im/sonata-nfv/Lobby.svg)](https://gitter.im/sonata-nfv/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
