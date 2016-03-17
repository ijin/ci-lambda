echo "generating for template" >> /tmp/l.log
cwd=`dirname "${0}"`
pushd $cwd
cp ../environment.py .
finalize
zip -J -X -r ./lambda.zip sample.py env.json environment.py
echo "zipped template" >> /tmp/l.log
popd

