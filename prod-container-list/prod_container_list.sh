#!/usr/bin/env bash

# OPS-3804 Provide list of productive containers
# As response to the audit result of the Schulcloud project, we need to provide a joined list of all containers running the several CLUSTER_LIST types of the PROD area.
# We have to list the container type, e.g. api-server the image currently active in the CLUSTER_LIST and whether the container runs stateless or stateful.

set -Eeuo pipefail
trap EXIT

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

FILE=$SCRIPT_DIR"/ProdContainerList_"`date +%y%m%d`".csv"
LOG=$SCRIPT_DIR"/ProdContainerList_"`date +%y%m%d`".log"
CLUSTER_LIST=("sc-prod-admin.yaml" "sc-prod-collaboration.yaml" "sc-prod-legacy.yaml" "sc-prod-nextcloud.yaml" "sc-prod-servicecenter.yaml")
IMAGE_COUNT=0
TOTAL_IMAGE_COUNT=0

# file header
echo "CLUSTER_LIST;CONTAINER_IMAGE;STATE_TYPE_PVC" > $FILE
echo $LOG > $LOG

for CLUSTER_ITEM in ${CLUSTER_LIST[*]}
do
    echo "Processing:"${CLUSTER_ITEM%.*} | tee -a $LOG
    CLUSTER_IMAGE_LIST=($(kubectl get pods --kubeconfig ~/.kube/$CLUSTER_ITEM --all-namespaces -o jsonpath='{range .items[*]}{"\n"}{.spec.containers[*].image}{.spec.volumes[*].persistentVolumeClaim}{end}' | sed 's/ //g' | sort | uniq))
    IMAGE_COUNT=0

    for IMAGE_ITEM in ${CLUSTER_IMAGE_LIST[*]}
    do
        STATE_TYPE_PVC=false
        if [[ ! $IMAGE_ITEM == ${IMAGE_ITEM%{*} ]]
        then
            STATE_TYPE_PVC=true
            IMAGE_ITEM=${IMAGE_ITEM%{*}
        fi       
        echo "${CLUSTER_ITEM%.*};$IMAGE_ITEM;$STATE_TYPE_PVC" >> $FILE
        IMAGE_COUNT=$((IMAGE_COUNT+1))
    done
    
    echo "Cluster Image Count:"$IMAGE_COUNT | tee -a $LOG
    TOTAL_IMAGE_COUNT=$((TOTAL_IMAGE_COUNT + IMAGE_COUNT))

done

echo "Total Images Count:"$TOTAL_IMAGE_COUNT | tee -a $LOG

exit
