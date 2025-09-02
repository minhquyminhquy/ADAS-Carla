"""
This script plots the spawnpoints and the road networks for pre-route planning.

Designed for Town10 in Carla 0.10.0
"""

import carla
import matplotlib.pyplot as plt

def main():
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0) 
        world = client.get_world()
        carla_map = world.get_map()

        if 'Town10HD_Opt' not in carla_map.name:
            print(f"Map name is wrong!")
            
        print(f"Fetching data for map: {carla_map.name}")

        topology = carla_map.get_topology()
        spawn_points = carla_map.get_spawn_points()

        road_lines = []
        for waypoint_pair in topology:
            start_point = waypoint_pair[0].transform.location
            end_point = waypoint_pair[1].transform.location
            road_lines.append([
                (start_point.x, start_point.y), 
                (end_point.x, end_point.y)
            ])

        spawn_point_coords = []
        for sp_transform in spawn_points:
            loc = sp_transform.location
            spawn_point_coords.append((loc.x, loc.y))

        fig, ax = plt.subplots(figsize=(20, 20))

        print("Plotting road network...")
        for line in road_lines:
            (x1, y1), (x2, y2) = line
            ax.plot([x1, x2], [y1, y2], color='gray', linestyle='-', linewidth=0.5)

        # Plot all spawn points as large red dots
        print(f"Plotting {len(spawn_points)} spawn points...")
        sp_x, sp_y = zip(*spawn_point_coords)
        ax.scatter(sp_x, sp_y, color='red', s=50, label='Spawn Points', zorder=5)

        # Add index labels for each spawnpoint
        print("Adding index labels to spawn points...")
        for i, coords in enumerate(spawn_point_coords):
            x, y = coords
            ax.text(x + 5, y + 5, str(i), fontsize=9, color='darkblue', zorder=6,
                    ha='center', va='center', weight='bold')

        ax.set_title(f'CARLA Map: {carla_map.name} - Road Network & Spawn Points with Indices', fontsize=20)
        ax.set_xlabel('X (meters)', fontsize=14)
        ax.set_ylabel('Y (meters)', fontsize=14)
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
        
        ax.set_aspect('equal', adjustable='box')
        
        ax.invert_yaxis()

        print("Displaying map plot. Close the plot window to exit the script.")
        plt.show()

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == '__main__':
    main()