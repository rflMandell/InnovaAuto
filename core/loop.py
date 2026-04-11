# o loopzao louco q faz a porra toda funcionar
import time
from engine.car_state import CarState
from engine.gearbox import Gearbox
from engine.motor import Motor
from engine.velocity import Velocity
from sensors.vehicle_sensors import VehicleSensors
from input.controller import ControllerInput

TICK_RATE = 5

def run():
    state = CarState()
    controller = ControllerInput()
    gearbox = Gearbox()
    motor = Motor()
    velocity = Velocity()
    sensors = VehicleSensors()
    
    tick_interval = 1.0 / TICK_RATE

    #controle de tempo para delta_time
    last_time = time.time()
    
    print("=" * 50)
    print("InnovaAuto - Sistema Iniciado")
    print(f"Tick rate: {TICK_RATE}/s | Pressione Ctrl+C para sair")
    print("=" * 50)

    try:
        while state.running:
            now = time.time()
            delta_time = now - last_time()
            last_time = now

            # -- Leitura do controle --
            controller.update(state, gearbox)
            gearbox.update(state)
            motor.update(state, delta_time)
            velocity.update(state, delta_time)
            sensors.update(state, delta_time)

            # Exibe estado atual no terminal
            _print_state(state)

            #controla o tempo para manter o tick constante
            elapsed = time.time() - now
            sleep_time = tick_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n\nSistema encerrado.")
    finally:
        controller.quit()
        
def _print_state(state):
    """Exibe o estado atual do carro de forma organizada no terminal."""
    
    rpm_bar  = _build_bar(state.rpm, 0, 7000, length=10)
    spd_bar  = _build_bar(state.speed, 0, 220, length=10)
    fuel_bar = _build_bar(state.fuel, 0, 100, length=10)
    temp_bar = _build_bar(state.oil_temp, 20, 150, length=10)

    # Ícones de status
    rpm_icon  = "🔴" if state.rpm >= 6500 else ("🟡" if state.rpm >= 5000 else "🟢")
    
    fuel_icon = "⛽🔴" if state.fuel <= 15 else "⛽"
    
    temp_icon = "🌡️🔴" if state.oil_temp >= 110 else ("🌡️🟡" if state.oil_temp >= 90 else "🌡️🟢")
    
    ce_icon   = " CHECK ENGINE" if state.check_engine else ""

    shifting_tag = "AGUARDE" if state.shifting else "  "

    print(
        f"\r"
        f"[{state.gear:>2}]{shifting_tag} "
        f"RPM:{state.rpm:>5.0f}{rpm_icon}{rpm_bar} "
        f"Vel:{state.speed:>6.1f}km/h {spd_bar} "
        f"{fuel_icon}{state.fuel:>5.1f}% {fuel_bar} "
        f"Auto:{state.autonomy:>5.0f}km "
        f"{temp_icon}{state.oil_temp:>5.1f}°C {temp_bar}"
        f"{ce_icon}   ",
        end=""
    )
        
def _build_bar(value, min_val, max_val, length=15):
    """Gera uma barra de progresso visual para o terminal"""
    ratio = (value - min_val) / (max_val - min_val)
    ratio = max(0.0, min(ratio, 1.0))
    filled = int(ratio* length)
    return "[" + "█" * filled + "░" * (length - filled) + "]"