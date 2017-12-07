using System;
using System.Threading;
using Amazon.Lambda.Core;
using Amazon.Lambda.Serialization.Json;
using System.Diagnostics;

namespace TimeoutLambda
{
	public class Handler
	{
		[LambdaSerializer(typeof(JsonSerializer))]
			public Result Handle(Request request) {
				var stopwatch = new Stopwatch();
				stopwatch.Start();
				System.Threading.Thread.Sleep(1000);
				stopwatch.Stop();
				var elapsed_time = stopwatch.ElapsedMilliseconds;
				return new Result {
					ElapsedTime = elapsed_time
				};
			}
	}
	public class Request
	{
		public string Second { get; set; }
	}

	public class Result
	{
		public long ElapsedTime { get; set; }
	}
}

