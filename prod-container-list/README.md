# prod container list

## Provide list of productive containers OPS-3804 

As response to the audit result of the Schulcloud project, we need to provide a joined list of all containers running the several CLUSTER_LIST types of the PROD area.
We have to list the container type, e.g. api-server the image currently active in the CLUSTER_LIST and whether the container runs stateless or stateful.

## preconditions

script needs kubeconfigs:
sc-prod-admin.yaml
sc-prod-collaboration.yaml
sc-prod-legacy.yaml
sc-prod-nextcloud.yaml
sc-prod-servicecenter.yaml
available under ~/.kube/
## create Container List 

run shell script in folder /infra-tools/prod-container-list/
```
bash prod_container_list.sh
```
