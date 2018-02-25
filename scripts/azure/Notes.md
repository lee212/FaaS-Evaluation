# Concurrency Test

Azure has its own scaling controller to increase instances based on the input event sizes. We performed 3 tests to verify how it works with configurations and found some caveats to understand.

## Caveats

- Experimental languages may not work as expected e.g. Python
- C#, F# and Javascript are supported languages
- Event Hub is for handling large concurrent event messages
- Queue storage trigger supports up to 32 batch sizes to process at a time
- Log messages might be throttled if it exceeds thresholds

## Resources

- Functions Scale: https://docs.microsoft.com/en-us/azure/azure-functions/functions-scale
- Event Hubs: https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs#trigger---scaling
- HTTP Concurrency host options: https://docs.microsoft.com/en-us/azure/azure-functions/functions-best-practices#scalability-best-practices
- host.json: https://github.com/Azure/azure-functions-host/wiki/host.json
- host.json(Queues): https://docs.microsoft.com/en-us/azure/azure-functions/functions-host-json#queues
