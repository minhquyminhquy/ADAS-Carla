import carla
import time
import random
import numpy as np
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CarlaClient:
    def __init__(self, host: str = "localhost", port: int = 2000, timeout: float = 10.0):
        """Initialize Carla client with connection parameters."""
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client = None
        self.world = None
        self.vehicle = None
        self.sensors = {}
        self.blueprint_library = None
        
    def connect(self) -> bool:
        """Connect to Carla server."""
        try:
            self.client = carla.Client(self.host, self.port)
            self.client.set_timeout(self.timeout)
            self.world = self.client.get_world()
            self.blueprint_library = self.world.get_blueprint_library()
            logger.info(f"Connected to Carla server at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Carla: {e}")
            return False
    
    def load_world(self, map_name: str = "Town01") -> bool:
        """Load a specific world/map."""
        try:
            self.world = self.client.load_world(map_name)
            self.blueprint_library = self.world.get_blueprint_library()
            logger.info(f"Loaded world: {map_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to load world {map_name}: {e}")
            return False
    
    def spawn_vehicle(self, vehicle_model: str = "vehicle.tesla.model3", 
                     spawn_point: Optional[carla.Transform] = None) -> bool:
        """Spawn a vehicle at specified location or random location."""
        try:
            # Get vehicle blueprint
            vehicle_bp = self.blueprint_library.find(vehicle_model)
            if not vehicle_bp:
                logger.warning(f"Vehicle {vehicle_model} not found, using default")
                vehicle_bp = self.blueprint_library.find("vehicle.tesla.model3")
            
            # Set spawn point
            if spawn_point is None:
                spawn_points = self.world.get_map().get_spawn_points()
                spawn_point = random.choice(spawn_points)
            
            # Spawn vehicle
            self.vehicle = self.world.spawn_actor(vehicle_bp, spawn_point)
            logger.info(f"Spawned vehicle {vehicle_model} at {spawn_point.location}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to spawn vehicle: {e}")
            return False
    
    def setup_sensors(self) -> bool:
        """Setup basic sensors for ADAS system."""
        if not self.vehicle:
            logger.error("No vehicle available for sensor setup")
            return False
        
        try:
            # Camera sensor
            camera_bp = self.blueprint_library.find('sensor.camera.rgb')
            camera_bp.set_attribute('image_size_x', '1920')
            camera_bp.set_attribute('image_size_y', '1080')
            camera_bp.set_attribute('fov', '90')
            
            camera_location = carla.Location(x=2.0, z=1.4)
            camera_rotation = carla.Rotation(pitch=-15)
            camera_transform = carla.Transform(camera_location, camera_rotation)
            
            camera = self.world.spawn_actor(camera_bp, camera_transform, attach_to=self.vehicle)
            self.sensors['camera'] = camera
            logger.info("Camera sensor setup complete")
            
            # IMU sensor
            imu_bp = self.blueprint_library.find('sensor.other.imu')
            imu_location = carla.Location(x=0.0, z=0.0)
            imu_transform = carla.Transform(imu_location)
            
            imu = self.world.spawn_actor(imu_bp, imu_transform, attach_to=self.vehicle)
            self.sensors['imu'] = imu
            logger.info("IMU sensor setup complete")
            
            # GPS sensor
            gps_bp = self.blueprint_library.find('sensor.other.gnss')
            gps_location = carla.Location(x=0.0, z=0.0)
            gps_transform = carla.Transform(gps_location)
            
            gps = self.world.spawn_actor(gps_bp, gps_transform, attach_to=self.vehicle)
            self.sensors['gps'] = gps
            logger.info("GPS sensor setup complete")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup sensors: {e}")
            return False
    
    def set_weather(self, weather_type: str = "ClearNoon"):
        """Set weather conditions."""
        weather_presets = {
            "ClearNoon": carla.WeatherParameters.ClearNoon,
            "CloudyNoon": carla.WeatherParameters.CloudyNoon,
            "WetNoon": carla.WeatherParameters.WetNoon,
            "WetCloudyNoon": carla.WeatherParameters.WetCloudyNoon,
            "MidRainyNoon": carla.WeatherParameters.MidRainyNoon,
            "HardRainNoon": carla.WeatherParameters.HardRainNoon,
            "SoftRainNoon": carla.WeatherParameters.SoftRainNoon,
            "ClearSunset": carla.WeatherParameters.ClearSunset,
            "CloudySunset": carla.WeatherParameters.CloudySunset,
            "WetSunset": carla.WeatherParameters.WetSunset,
            "WetCloudySunset": carla.WeatherParameters.WetCloudySunset,
            "MidRainSunset": carla.WeatherParameters.MidRainSunset,
            "HardRainSunset": carla.WeatherParameters.HardRainSunset,
            "SoftRainSunset": carla.WeatherParameters.SoftRainSunset,
        }
        
        if weather_type in weather_presets:
            self.world.set_weather(weather_presets[weather_type])
            logger.info(f"Weather set to: {weather_type}")
        else:
            logger.warning(f"Weather type {weather_type} not found, using ClearNoon")
            self.world.set_weather(carla.WeatherParameters.ClearNoon)
    
    def enable_autopilot(self, enabled: bool = True):
        """Enable or disable autopilot."""
        if self.vehicle:
            self.vehicle.set_autopilot(enabled)
            status = "enabled" if enabled else "disabled"
            logger.info(f"Autopilot {status}")
    
    def manual_control(self, throttle: float = 0.0, steer: float = 0.0, brake: float = 0.0):
        """Apply manual control to the vehicle."""
        if self.vehicle:
            control = carla.VehicleControl()
            control.throttle = np.clip(throttle, 0.0, 1.0)
            control.steer = np.clip(steer, -1.0, 1.0)
            control.brake = np.clip(brake, 0.0, 1.0)
            self.vehicle.apply_control(control)
    
    def get_vehicle_state(self) -> Dict:
        """Get current vehicle state information."""
        if not self.vehicle:
            return {}
        
        transform = self.vehicle.get_transform()
        velocity = self.vehicle.get_velocity()
        acceleration = self.vehicle.get_acceleration()
        
        return {
            'location': {
                'x': transform.location.x,
                'y': transform.location.y,
                'z': transform.location.z
            },
            'rotation': {
                'pitch': transform.rotation.pitch,
                'yaw': transform.rotation.yaw,
                'roll': transform.rotation.roll
            },
            'velocity': {
                'x': velocity.x,
                'y': velocity.y,
                'z': velocity.z
            },
            'acceleration': {
                'x': acceleration.x,
                'y': acceleration.y,
                'z': acceleration.z
            }
        }
    
    def cleanup(self):
        """Clean up all spawned actors."""
        logger.info("Cleaning up Carla actors...")
        
        # Destroy sensors
        for sensor_name, sensor in self.sensors.items():
            if sensor and sensor.is_alive:
                sensor.destroy()
                logger.info(f"Destroyed sensor: {sensor_name}")
        
        # Destroy vehicle
        if self.vehicle and self.vehicle.is_alive:
            self.vehicle.destroy()
            logger.info("Destroyed vehicle")
        
        self.sensors.clear()
        self.vehicle = None

def main():
    """Main function to demonstrate basic Carla setup."""
    # Create and connect client
    client = CarlaClient()
    
    if not client.connect():
        logger.error("Failed to connect to Carla server")
        return
    
    # Load world
    if not client.load_world("Town01"):
        logger.error("Failed to load world")
        return
    
    # Set weather
    client.set_weather("ClearNoon")
    
    # Spawn vehicle
    if not client.spawn_vehicle():
        logger.error("Failed to spawn vehicle")
        return
    
    # Setup sensors
    if not client.setup_sensors():
        logger.error("Failed to setup sensors")
        return
    
    # Enable autopilot for demonstration
    client.enable_autopilot(True)
    
    try:
        logger.info("Carla setup complete! Vehicle is running with autopilot.")
        logger.info("Press Ctrl+C to stop...")
        
        # Main loop - keep the simulation running
        while True:
            # Get and log vehicle state every 5 seconds
            state = client.get_vehicle_state()
            if state:
                logger.info(f"Vehicle location: {state['location']}")
                logger.info(f"Vehicle velocity: {state['velocity']}")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        logger.info("Stopping simulation...")
    finally:
        client.cleanup()
        logger.info("Simulation stopped and cleaned up.")

if __name__ == "__main__":
    main()