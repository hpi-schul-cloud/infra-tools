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


HELMDOCSIGNORE_EXISTED=""
FILE=$BASE_PATH/.helmdocsignore
if test -f "$FILE"; then
    echo "$FILE exists."
    HELMDOCSIGNORE_EXISTED="true"
else 
    echo "Creating .helmdocsignore file"
    touch .helmdocsignore
    HELMDOCSIGNORE_EXISTED="false"
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


# delete helmignore file if it didn't existed prior
if [ "${HELMDOCSIGNORE_EXISTED}" == "false" ]
then 
    rm -f $BASE_PATH/.helmdocsignore
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
        echo "Changes detected - will commit and push generated README.md's"
        git add \*.md
        git commit --message "${COMMIT_MESSAGE}"
        git push origin 
    else
        echo "Changes detected - will not commit or push changes"

    fi
fi

echo "Complete 🟢"

