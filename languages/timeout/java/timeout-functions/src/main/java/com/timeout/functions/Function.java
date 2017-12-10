/*
 * https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-java-maven
 */
package com.timeout.functions;

import java.util.*;
import com.microsoft.azure.serverless.functions.annotation.*;
import com.microsoft.azure.serverless.functions.*;

/**
 * Azure Functions with HTTP Trigger.
 */
public class Function {
    /**
     * This function listens at endpoint "/api/hello". Two ways to invoke it using "curl" command in bash:
     * 1. curl -d "HTTP Body" {your host}/api/hello
     * 2. curl {your host}/api/hello?name=HTTP%20Query
     */
    @FunctionName("timeout")
    public HttpResponseMessage<String> timeout(
            @HttpTrigger(name = "req", methods = {"get", "post"}, authLevel = AuthorizationLevel.ANONYMOUS) HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {
        context.getLogger().info("Java HTTP trigger processed a request.");

        // Parse query parameter
        String second = request.getQueryParameters().get("second");
	context.getLogger().info(second);

	try {
		Thread.sleep(Integer.parseInt(second)*1000);                 //1000 milliseconds is one second.
	} catch(InterruptedException ex) {
		Thread.currentThread().interrupt();
		
	}

        if (second == null) {
            return request.createResponse(400, "Please pass a second on the query string or in the request body");
        } else {
            return request.createResponse(200, "Thread.sleep in " + second + "second(s)");
        }
    }
}
