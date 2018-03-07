# Concurrent Test

We ran a couple of tests to measure concurrent throughput of AWS Lambdas with S3 which stores results in a file.
What we found that is:

- AWS Logs are throttled when it reaches at a certain limits.
  e.g. we ran 16500 invocations but 16400 are recorded
- S3 takes extra time to store an object from its request.
  e.g. 500 invocation was done in 1-2 seconds according to AWS logs but S3 created time shows +9 seconds between the first object and the last object written.

## Extra Tips

- Concurrency limit is account based, for example 1000 is default for account A,
	if x concurrency is reserved for function a, other functions can use upto 1000 - x concurrency.
