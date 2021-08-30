import paramiko
import sshtunnel

def openTunnel (jumphost, jumphost_user, api_server_host, api_server_port):

    ssh_pkey=paramiko.agent.Agent().get_keys()
    with sshtunnel.open_tunnel(
        (jumphost, 22),
        ssh_username=jumphost_user,
        ssh_pkey=paramiko.agent.Agent().get_keys(),
        #ssh_pkey="/var/ssh/rsa_key",
        #ssh_private_key_password="secret",
        remote_bind_address=(api_server_host, api_server_port),
        local_bind_address=('0.0.0.0', api_server_port), 
        host_pkey_directories = []
    ) as server:
        def do_something(port):
            # Here we have to wait
            pass

        print("LOCAL PORTS:", server.local_bind_port)

        do_something(server.local_bind_port)
        pass
