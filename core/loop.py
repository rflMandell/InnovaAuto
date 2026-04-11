import time
import threading
from engine.car_state import CarState
from engine.gearbox import Gearbox
from engine.motor import Motor
from engine.velocity import Velocity
from sensors.vehicle_sensors import VehicleSensors
from faults.fault_manager import FaultManager
from input.controller import ControllerInput

TICK_RATE = 30


def run(state):
    """
    Loop de simulação — roda em thread separada.
    Recebe o CarState já criado para compartilhar com a UI.
    """
    controller = ControllerInput()
    gearbox = Gearbox()
    motor = Motor()
    velocity = Velocity()
    sensors = VehicleSensors()
    faults = FaultManager()

    gearbox.fault_manager = faults

    tick_interval = 1.0 / TICK_RATE
    last_time = time.time()

    try:
        while state.running:
            now = time.time()
            delta_time = now - last_time
            last_time = now

            controller.update(state, gearbox)
            gearbox.update(state)
            motor.update(state, delta_time)
            velocity.update(state, delta_time)
            sensors.update(state, delta_time)
            faults.update(state, delta_time)

            elapsed = time.time() - now
            sleep_time = tick_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except Exception as e:
        print(f"\nErro no loop de simulação: {e}")
    finally:
        controller.quit()
        print("\nSimulação encerrada.")


def start_simulation_thread(state):
    """Inicia o loop de simulação em background."""
    t = threading.Thread(target=run, args=(state,), daemon=True)
    t.start()
    return t