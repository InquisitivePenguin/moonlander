import asyncio
from typing import Optional
from .utils import DEG_TO_METER_RATIO
from mavsdk import System
from mavsdk.telemetry import Position, Health, GpsInfo, Battery

class Drone:
    """
    A wrapper over MavSDK-Python's System class that automatically manages receiving telemetry information
    and executing commands.
    """
    def __init__(self, mavsdk_server_address=None, port=50051):
        self.drone = System(mavsdk_server_address=mavsdk_server_address, port=port)
        self.status = Status()
        self.handler_routines = []
        self.armed = False

    async def connect(self, address="udp://:14540"):
        await self.drone.connect(system_address=address)
        print("Waiting for drone to connect...")
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                print("Drone discovered!")
                break
        # Set up telemetry handlers
        self.handler_routines = [
            asyncio.ensure_future(self.__update_health()),
            asyncio.ensure_future(self.__update_battery()),
            asyncio.ensure_future(self.__update_position()),
            asyncio.ensure_future(self.__update_gps_info()),
            asyncio.ensure_future(self.__update_home())
        ]

        # Wait for telemetry to be fully initialized
        while not self.status.initialized():
            await asyncio.sleep(1)
        print("Telemetry initialized")

    async def __update_health(self):
        async for health in self.drone.telemetry.health():
            self.status.health = health

    async def __update_battery(self):
        async for battery in self.drone.telemetry.battery():
            self.status.battery = battery

    async def __update_position(self):
        async for position in self.drone.telemetry.position():
            self.status.position = position

    async def __update_gps_info(self):
        async for gps_info in self.drone.telemetry.gps_info():
            self.status.gps_info = gps_info

    async def __update_home(self):
        async for home in self.drone.telemetry.home():
            self.status.home = home

    async def __update_in_air(self):
        async for in_air in self.drone.telemetry.in_air():
            self.status.in_air = in_air

    # TODO: return a commander class that provides an interface
    # to the drone commands
    async def arm(self):
        # Perform pre-flight check
        if self.status.health.is_global_position_ok:
            print("Global position estimate ok")

        await self.drone.action.arm()
        self.armed = True

    # TODO: put this inside of the commander class
    async def takeoff(self):
        assert self.armed
        await self.drone.action.takeoff()

    # TODO: put this inside of the commander class
    async def goto_position_from_home(self, relative_latitude, relative_longitude, altitude, threshold=0.01/DEG_TO_METER_RATIO):
        """
        Go to a longitude, latitude, and altitude relative to the drone's home position.
        Will continue executing until the drone comes within `threshold` degrees of the target coordinates
        """
        assert self.armed

        # Get home position
        home = self.status.home
        latitude, longitude, absolute_altitude = home.latitude_deg, home.longitude_deg, home.absolute_altitude_m

        goto_latitude = latitude + relative_latitude
        goto_longitude = longitude + relative_longitude

        await self.drone.action.goto_location(goto_latitude, goto_longitude, absolute_altitude + altitude, 0)

        while abs(self.status.position.latitude_deg - goto_latitude) > threshold and abs(self.status.position.longitude_deg - goto_longitude) > threshold:
            await asyncio.sleep(1)
        print("Reached destination")

    # TODO: put this inside of the commander class
    async def land(self):
        assert self.armed
        await self.drone.action.land()


class Status:
    position: Optional[Position]
    gps_info: Optional[GpsInfo]
    battery: Optional[Battery]
    health: Optional[Health]
    home: Optional[Position]
    in_air: bool

    def __init__(self):
        self.position = None
        self.gps_info = None
        self.battery = None
        self.health = None
        self.home = None
        self.in_air = False

    def initialized(self):
        return self.position is not None and self.gps_info is not None and self.battery is not None and self.health is not None and self.home is not None
