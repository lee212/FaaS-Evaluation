# For Azure Functions

using System.Net;
using System.Diagnostics;

public static class Globals
{ 
    public static String Init = "True";
}

public static long FindPrimeNumber(int n)
{
    int count=0;
    long a = 2;
    while(count<n)
    {
        long b = 2;
        int prime = 1;// to check if found a prime
        while(b * b <= a)
        {
            if(a % b == 0)
            {
                prime = 0;
                break;
            }
            b++;
        }
        if(prime > 0)
        {
            count++;
        }
        a++;
    }
    return(--a);
}

public static async Task<HttpResponseMessage> Run(HttpRequestMessage req, TraceWriter log)
{
    //log.Info("C# HTTP trigger function processed a request.");
    string seqid = req.GetQueryNameValuePairs()
        .FirstOrDefault(q => string.Compare(q.Key, "seqid", true) == 0)
        .Value;
    string cid = req.GetQueryNameValuePairs()
        .FirstOrDefault(q => string.Compare(q.Key, "cid", true) == 0)
        .Value;
    
    // parse query parameter
    string num = req.GetQueryNameValuePairs()
        .FirstOrDefault(q => string.Compare(q.Key, "num", true) == 0)
        .Value;
    
    if (num == null)
    {
        // Get request body
        dynamic data = await req.Content.ReadAsAsync<object>();
        num = data?.num;
        seqid = data?.seqid;
        cid = data?.cid;
    }

    var stopwatch = new Stopwatch();
    stopwatch.Start();
    int numInt = Convert.ToInt32(num);
    long nthPrime = FindPrimeNumber(numInt);
    stopwatch.Stop();
    var elapsed_time = stopwatch.ElapsedMilliseconds;
    log.Info(cid + "," + seqid +"," + num + "," + elapsed_time + "," + Globals.Init + ",v2");
    Globals.Init = "False";
    return num == null
        ? req.CreateResponse(HttpStatusCode.BadRequest, "Please pass a name on the query string or in the request body")
        : req.CreateResponse(HttpStatusCode.OK, "Hello " + num + "," + nthPrime );
}

