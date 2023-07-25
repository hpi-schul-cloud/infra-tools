# awx-ee

In this repository we configure our AWX Execution Environment. An execution environment is simply a docker image with preinstalled ansible dependencies and tools to have them available during an ansible run in AWX. As some tools (e.g. terraform, helm,) cannot be installed in the default execution environment a custom exection environment was created.
The Dockerfile is automatically create by the execution-environment.yml 

## Ansible Builder 
We use Ansible Builder to generate the Dockerfile. For the ansible-builder version 3 at least python 3.9 is required. Run this commmand and the Dockerfile gets created/updated. 

```
ansible-builder build -c . --tag=<sometag> 
```
The files in the folder _build/scrpt/* are also created and maintained by ansible-builder. 

## Documentation
- [Confluence](https://docs.dbildungscloud.de/display/PROD/AWX+Execution+Environment) 
- [ansible-builder Docs](https://ansible.readthedocs.io/projects/builder/en/stable/definition/)
- [ansible-builder Github](https://github.com/ansible/ansible-builder)
