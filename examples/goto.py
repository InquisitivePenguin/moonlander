import asyncio
from moonlander import Drone
from moonlander.utils import meters_to_deg

async def main():
    drone = Drone()
    await drone.connect()
    await drone.arm()

    await drone.takeoff()

    await drone.goto_position_from_home(meters_to_deg(5), meters_to_deg(5), 5)

    await drone.land()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())