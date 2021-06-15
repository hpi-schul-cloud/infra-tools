# Ansible Collection - schulcloud.onepwd

## List of roles
- schulcloud.haproxy.basic: installs haproxy and haproxy exporter. variables:
    - haproxy_config_template: path to the haproxy config template to use. possible values:
        - haproxy.cfg.j2: default value, the default haproxy configuration without any frontends or backends
        - backend-haproxy.cfg.j2: backend haproxy configuration. variables:
            - frontend_ips: list of the IPs of the frontend NICs of the backend haproxy
            - k8s_node_ips: list of the IPs of the nodes of the backend kubernetes cluster
        - "{{ playbook_dir }}/\<path to another template\>"
- schulcloud.haproxy.backend_haproxy: configures the haproxy to be used as a backend haproxy. variables:
    - privatelan_network_interfaces: list of the network interfaces that the haproxy is listening on where port 80 will be opened
