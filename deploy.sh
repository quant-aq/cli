# https://python-poetry.org/docs/cli/#version

# Tag the version
if [ -z "$1" ]
    then 
        echo "Deploy failed"
elif [ "$1" = "patch" ]
    then 
        poetry version patch
elif [ "$1" = "minor" ]
    then 
        poetry version minor
elif [ "$1" = "major" ]
    then
        poetry version major
elif [ "$1" = "premajor" ]
    then
        poetry version premajor
elif [ "$1" = "preminor" ]
    then
        poetry version preminor
elif [ "$1" = "prepatch" ]
    then
        poetry version prepatch
elif [ "$1" = "prerelease" ]
    then
        poetry version prerelease
else
    echo "Deploy failed."
fi

# Tag
VERSION=`poetry version`
VERSION_BITS=(${VERSION//  })
NEW_TAG=${VERSION_BITS[1]}

# commit the changes
git add -A
git commit -m "Pushing a new release candidate"

# get the previous version
PREV_VERSION=`git describe --abbrev=0 --tags`

GIT_COMMIT=`git rev-parse HEAD`
NEEDS_TAG=`git describe --contains $GIT_COMMIT 2>/dev/null`

# create a new tag
if [ -z "$NEEDS_TAG" ]; then
    # git tag $NEW_TAG
    echo "Tagged with $NEW_TAG"
    # git push --tags
else 
    echo "Already a tag on this commit"
fi