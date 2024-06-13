#!/bin/bash

# Check if a version number argument is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <version_number>"
    exit 1
fi

VERSION=$1

# Commands to add files, commit, tag, and push
git add .
git commit -m "v$VERSION"
git tag -a "v$VERSION" -m "Version $VERSION"
git push origin master --tags


# RUN with the command ./deploy.sh <version_number>
