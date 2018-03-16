# BigData-Benchmark

BigData Benchark experiment on IBM OpenWhisk Functions

## Scan Query

First experiment is a simple scan query with 100 ranking files from pavlo dataset.

### BX CLI

The following commands are to build functions using bx command line tools.

```
echo "ibm-cos-sdk" > requirements.txt
sudo  docker run --rm -v "$PWD:/tmp" ibmfunctions/action-python-v3    bash  -c "cd tmp && virtualenv virtualenv && source virtualenv/bin/activate && pip install -r requirements.txt"
zip -r bigdata-scanner.zip virtualenv __main__.y
bk action create bigdata-scanner --kind python:3 bigdata-scanner.zip -m 512 -t 300000
bx wsk action invoke bigdata-scanner -P param
```
