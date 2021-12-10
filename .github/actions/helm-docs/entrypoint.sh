#!/bin/bash

# ENVS FROM ACTION YAML 
PERSONAL_TOKEN="$INPUT_PERSONAL_TOKEN"
SRC_PATH="$INPUT_SRC_PATH"
COMMIT_MESSAGE="$INPUT_COMMIT_MESSAGE"
USERNAME="$INPUT_USERNAME"
EMAIL="$INPUT_EMAIL"
TEMPLATE_FILE="$INPUT_TEMPLATE_FILE"
IGNORED_DIRS="$INPUT_IGNORED_DIRS"
GIT_PUSH="$INPUT_GIT_PUSH"
# OTHER ENVS
BASE_PATH=$(pwd)


echo "-----Information:---------------------------"
git --version
helm-docs --version
echo "Base path is: $BASE_PATH"
if [ "${TEMPLATE_FILE}" != "" ]
then
    echo "Templates file location is: $TEMPLATE_FILE"
else
    echo "Template file is not provided"
fi

echo "----.helmdocsignore Status:----------------"

FILE=$(pwd)/.helmdocsignore
if test -f "$FILE"; then
    echo "$FILE exists."
else 
    echo "Creating .helmdocsignore file"
    touch .helmdocsignore
fi

# Updating .helmdocsignore file
IFS=',' ;for DIR in ${IGNORED_DIRS}
do 
    if grep -Fxq "$DIR" .helmdocsignore
    then 
        echo "$DIR already in ignored list"
    else 
        echo "$DIR" >> .helmdocsignore
        echo "$DIR added to the ignored list"
    fi 
done


echo "----Updating README.md files in specified dirs:------"
if [ "${TEMPLATE_FILE}" != "" ]
then 
    echo "Custom Template provided - using it"
    IFS=',' ;for DIR in `echo "$SRC_PATH"`;
    do 
        echo "Checking README.md recursively in dir: $BASE_PATH/$DIR"
        cd $BASE_PATH/$DIR
        helm-docs --log-level warning --template-files $BASE_PATH/${TEMPLATE_FILE}
    done
else 
    echo "Custom Template not provided - using default template"
    IFS=',' ;for DIR in `echo "$SRC_PATH"`;
    do 
        echo "Checking README.md recursively in dir: $BASE_PATH/$DIR"
        cd $BASE_PATH/$DIR
        helm-docs --log-level warning
    done
fi 

git config --global user.name "${USERNAME}"
git config --global user.email "${EMAIL}"

# Pushing Changes back to Repo 
if [ -z "$(git status --porcelain)" ]
then
    # Working directory is clean
    echo "No changes detected - nothing changed or pushed"
else
    echo "git_push is set to: ${GIT_PUSH}"
    if [ "${GIT_PUSH}" == "true" ]
    then 
        # commit and push changes
        echo "Changes detected - will commit and push"
        git add -A
        git commit --message "${COMMIT_MESSAGE}"
        git push origin 
    else
        echo "Changes detected - will not commit or push"

    fi
fi

echo "Complete 🟢"

