import carla
import random
import time

from typing import Tuple, Optional

def connect_to_carla(host: str, port: int, timeout: float, synchronous: bool = False, 
                    fixed_delta_seconds: float = 0.05) -> Tuple[Optional[carla.Client], Optional[carla.World]]:
    """
    Connect to a running Carla simulator
    
    Args:
        host: Carla server host
        port: Carla server port
        timeout: Connection timeout in seconds
        synchronous: If True, run CARLA in synchronous mode
        fixed_delta_seconds: Fixed time step for synchronous mode
        
    Returns:
        Tuple of (client, world) if connection successful, (None, None) otherwise
    """
    try:
        client = carla.Client(host, port)
        client.set_timeout(timeout)
        world = client.get_world()
        
        if synchronous:
            settings = world.get_settings()
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = fixed_delta_seconds
            world.apply_settings(settings)
            print(f"CARLA running in synchronous mode with {fixed_delta_seconds}s fixed time step")
            
        return client, world
    except Exception as e:
        print(f"Error connecting to Carla: {e}")
        return None, None
        
def spawn_vehicle(world: carla.World, vehicle_type: str = None) -> Optional[carla.Vehicle]:
    """
    Spawn a vehicle in the world
    
    Args:
        world: Carla world
        vehicle_type: Type of vehicle to spawn (e.g., 'model3')
        
    Returns:
        Vehicle actor if spawned successfully, None otherwise
    """
    try:
        blueprint_library = world.get_blueprint_library()
        
        if vehicle_type:
            vehicle_blueprint = blueprint_library.filter(vehicle_type)[0]
        else:
            vehicle_blueprint = random.choice(blueprint_library.filter('vehicle'))
            
        spawn_point = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(vehicle_blueprint, spawn_point)
        return vehicle
    except Exception as e:
        print(f"Error spawning vehicle: {e}")
        return None


def spawn_vehicles(world: carla.World, num_vehicles: int, vehicle_types: list[str] = None) -> None:
    """
    Spawn a number of vehicles in the world
    
    Args:
        world: Carla world
        num_vehicles: Number of vehicles to spawn
    """
    try:
        blueprint_library = world.get_blueprint_library()

        if vehicle_types:
            vehicle_blueprints = [blueprint_library.filter(vehicle_type)[0] for vehicle_type in vehicle_types]
        else:
            vehicle_blueprints = blueprint_library.filter('*vehicle*')
        
        spawn_points = world.get_map().get_spawn_points()
        
        for i in range(num_vehicles):
            try: 
                world.try_spawn_actor(random.choice(vehicle_blueprints), random.choice(spawn_points))
            except Exception as e:
                print(f"Error spawning vehicle: {e}")
                continue
    except Exception as e:
        print(f"Error spawning vehicles: {e}")
        return None
    
def set_autopilot(world: carla.World, enable: bool) -> None:
    """
    Set autopilot mode for all vehicles in the world
    
    Args:
        world: Carla world
    """
    try:
        for vehicle in world.get_actors().filter('*vehicle*'):
            vehicle.set_autopilot(enable)
    except Exception as e:
        print(f"Error setting autopilot: {e}")
        return None

def destroy_actors(world: carla.World) -> None:
    """
    Destroy all actors in the world
    
    Args:
        world: Carla world
    """
    try:
        for actor in world.get_actors():
            actor.destroy()
    except Exception as e:
        print(f"Error destroying actors: {e}")
        return None

def follow_vehicle(world: carla.World, vehicle: carla.Vehicle, stop_event=None) -> None:
    """
    Set spectator to follow a vehicle
    
    Args:
        world: Carla world object
        vehicle: Carla vehicle object
        stop_event: Threading event to signal when to stop following
    """
    spectator = world.get_spectator()
    
    camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
    camera_transform = carla.Transform(carla.Location(x=-4, z=4), carla.Rotation(pitch=-25))
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
    spectator.set_transform(camera.get_transform())

    try:
        while True:
            try:
                if stop_event and stop_event.is_set():
                    break
                    
                spectator.set_transform(camera.get_transform())
                time.sleep(0.01)
            except KeyboardInterrupt:
                print("\nCamera follow interrupted by user")
                break

    except Exception as e:
        print(f"Error setting spectator transform: {e}")
