import asyncio
from moonlander import Drone

async def main():
    drone = Drone()
    await drone.connect()
    await drone.arm()

    await drone.takeoff()

    await asyncio.sleep(5)

    await drone.land()

    print("Landed")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
