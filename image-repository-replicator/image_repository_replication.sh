#!/bin/bash

log_in_registry () {
  echo "log in with user $2 in registry $1"
  echo "$(crane auth login $1 -u $2 -p $3)"
}

get_repository_image_tags () {
  echo "$(crane ls $1)"
}

copy_repository () {
  while read -r image_tag ; do
    copy_image $1 $2 ${image_tag}
  done <<< "$image_tags"
}

copy_image () {
  crane cp $1:$3 $2:$3
}

start=`date +%s`

# Log in to the source registry to avoid pull limits
echo $(log_in_registry ${SOURCE_REPOSITORY_URL%%/*} ${SOURCE_REGISTRY_USER} ${SOURCE_REGISTRY_PASSWORD})

# Log in to the destination registry to get permission to push
echo $(log_in_registry ${DEST_REPOSITORY_URL%%/*} ${DEST_REGISTRY_USER} ${DEST_REGISTRY_PASSWORD})

image_tags="$(get_repository_image_tags ${SOURCE_REPOSITORY_URL})"
number_of_image_tags="$(wc -l <<< "$image_tags")"
echo "Copy ${number_of_image_tags} tagged images from repository ${SOURCE_REPOSITORY_URL} to ${DEST_REPOSITORY_URL}"
echo $(copy_repository ${SOURCE_REPOSITORY_URL} ${DEST_REPOSITORY_URL})

end=`date +%s`
runtime=$((end-start))
hours=$((runtime / 3600)); minutes=$(( (runtime % 3600) / 60 )); seconds=$(( (runtime % 3600) % 60 ));
echo "Copying of ${number_of_image_tags} tagged images from repository ${SOURCE_REPOSITORY_URL} to ${DEST_REPOSITORY_URL} took ${hours}h ${minutes}m ${seconds}s"