echo Commit: $1
echo Version: $2

rm -r milachan/__pycache__/
git add -A
git commit -m "$1"
git tag -a $2 -m "$1"
git push origin $2
git push origin master
python setup.py sdist upload -r pytest

