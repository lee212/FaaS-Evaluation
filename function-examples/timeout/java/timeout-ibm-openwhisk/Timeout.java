import com.google.gson.JsonObject;
public class Timeout{
    public static JsonObject main(JsonObject args) {
	int second = 1;
        if (args.has("second"))
            second = args.getAsJsonPrimitive("second").getAsInt();
	try {
		Thread.sleep(second*1000);                 //1000 milliseconds is one second.
	} catch(InterruptedException ex) {
		Thread.currentThread().interrupt();
	}

        JsonObject response = new JsonObject();
        response.addProperty("message", String.valueOf(second) + " elapsed");
        return response;
    }
}
