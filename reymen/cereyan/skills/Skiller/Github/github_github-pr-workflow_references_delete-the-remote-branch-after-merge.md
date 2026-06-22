# Delete the remote branch after merge
BRANCH=$(git branch --show-current)
git push origin --delete $BRANCH