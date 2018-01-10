package Timeout;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;

public class App implements RequestHandler<RequestClass, ResponseClass> {

	@Override
	public ResponseClass handleRequest(RequestClass input, Context context) {
		context.getLogger().log("Input: " + input.second);
		try {
			Thread.sleep(input.second*1000);                 //1000 milliseconds is one second.
		} catch(InterruptedException ex) {
			Thread.currentThread().interrupt();
		}

		return new ResponseClass(String.format("Time Thread sleep %s second", input.second));
	}

}
