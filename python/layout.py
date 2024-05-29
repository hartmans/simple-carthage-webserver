# Copyright (C) 2024, Hadron Industries.
# Carthage is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation. It is distributed
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the file
# LICENSE for details.


from carthage import *
from carthage.modeling import *
from carthage.ansible import *
from carthage.network import V4Config
from carthage_aws import *
from carthage_swf.models import PodmanMachine
from carthage.podman import *
from carthage.oci import *


class layout(CarthageLayout):

    add_provider(machine_implementation_key, dependency_quote(AwsVm))
    aws_instance_type = 't3.medium'
    class our_net(NetworkModel):
        v4_config = V4Config(network="192.168.100.0/24")
        aws_security_groups = ['dev']

    add_provider(InjectionKey("aws_ami"),
                 image_provider(name='Carthage-Debian*',
                                fallback=image_provider(owner=debian_ami_owner, name='debian-12-amd64-*')))

    class webserver(PodmanMachine, MachineModel):
        cloud_init = True
        class net_config(NetworkConfigModel):
            add('eth0', mac=None,
                net=InjectionKey("our_net"))
    

    class nginx_container(MachineModel):

        add_provider(podman_container_host, injector_access(InjectionKey('webserver')))
        add_provider(machine_implementation_key, dependency_quote(PodmanContainer))
        add_provider(oci_container_image, 'docker.io/library/nginx:latest')
        add_provider(OciExposedPort(container_port=80, host_port=80))
