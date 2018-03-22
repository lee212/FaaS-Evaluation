# IBM S3 - Object Storage

IBM Object storage is AWS S3-compatible service.

## Details

- CLI works like:

``aws --profile ibm --endpoint-url=https://s3.us-south.objectstorage.softlayer.net s3 ls``

The profile should be available in ```~/.aws/credentials``` like:

```
[ibm]
aws_access_key_id = 
aws_secret_access_key =
```

To obtain these credentials, Add Inline Configuration Parameters (Optional) field: ``{"HMAC":true};``
then a new credential has:   "cos_hmac_keys" field.

### No Public link?

It seems publicly downloadable link is not provided.
