# BigData Benchmark

This experiment runs the following items on Azure VMs and Functions both to compare its performance.

## Scan Query

Pavlo's rankings 100 files will be loaded from Azure Blob Storage.

### Details on building virtualenv for Functions

```
d:\Python27\Scripts\virtualenv.exe azure-storage-blob
cd azure-storage-blob\Scripts
activate.exe
easy_install.exe -U pip
pip install --upgrade setuptools
pip install azure-storage-blob
```
