import carla

def main():
    # Client creation
    client  = carla.Client("localhost", 2000)
    client.set_timeout(10.0)

    # World connection
    world = client.get_world()
    world = client.load_world('Town01')
    blueprint_library = world.get_blueprint_library()

    # Vehicle spawning and autopilot



    # Weather settings
    weather = carla.WeatherParameters(
        cloudiness=80.0,
        precipitation=30.0,
        sun_altitude_angle=70.0
    )
    world.set_weather(weather)

if __name__ == "__main__":
    main()