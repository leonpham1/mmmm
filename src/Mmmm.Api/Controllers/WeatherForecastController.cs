using Microsoft.AspNetCore.Mvc;

namespace Mmmm.Api.Controllers;

[ApiController]
[Route("api/v1/weather-forecasts")]
public class WeatherForecastController : ControllerBase
{
    private static readonly string[] Summaries =
    [
        "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
    ];
    
    [HttpGet(Name = "GetWeatherForecast")]
    [EndpointSummary("Get a list of weather forecasts for the next 5 days.")]
    [EndpointDescription("This endpoint returns **mock data** to illustrate the RESTful structure.")]
    [ProducesResponseType(typeof(IEnumerable<WeatherForecast>), StatusCodes.Status200OK)]
    public ActionResult<IEnumerable<WeatherForecast>> Get()
    {
        var forecasts = Enumerable.Range(1, 5).Select(index => new WeatherForecast
            {
                Date = DateOnly.FromDateTime(DateTime.Now.AddDays(index)),
                TemperatureC = Random.Shared.Next(-20, 55),
                Summary = Summaries[Random.Shared.Next(Summaries.Length)]
            })
            .ToArray();
        
        return Ok(forecasts); 
    }
}