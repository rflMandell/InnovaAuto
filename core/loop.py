import time
from engine.car_state import CarState
from engine.gearbox import Gearbox
from engine.motor import Motor
from engine.velocity import Velocity
from sensors.vehicle_sensors import VehicleSensors
from faults.fault_manager import FaultManager
from input.controller import ControllerInput

TICK_RATE = 5


def run():
    state = CarState()
    controller = ControllerInput()
    gearbox = Gearbox()
    motor = Motor()
    velocity = Velocity()
    sensors = VehicleSensors()
    faults = FaultManager()

    # Injeta o fault_manager no gearbox para checar transmissão
    gearbox.fault_manager = faults

    tick_interval = 1.0 / TICK_RATE
    last_time = time.time()

    print("=" * 50)
    print("  InnovaAuto — Sistema Iniciado")
    print(f"  Tick rate: {TICK_RATE}/s | Pressione Ctrl+C para sair")
    print("=" * 50)
    _print_fault_commands()

    try:
        while state.running:
            now = time.time()
            delta_time = now - last_time
            last_time = now

            # -- Módulos ativos --
            controller.update(state, gearbox)
            gearbox.update(state)
            motor.update(state, delta_time)
            velocity.update(state, delta_time)
            sensors.update(state, delta_time)
            faults.update(state, delta_time)

            # -- Exibição no terminal --
            _print_state(state)

            elapsed = time.time() - now
            sleep_time = tick_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n\nSistema encerrado pelo usuário. Até mais!")
    finally:
        controller.quit()


def _print_state(state):
    rpm_bar  = _build_bar(state.rpm,      0,   7000, length=10)
    spd_bar  = _build_bar(state.speed,    0,    220, length=10)
    fuel_bar = _build_bar(state.fuel,     0,    100, length=10)
    temp_bar = _build_bar(state.oil_temp, 20,   150, length=10)

    rpm_icon  = "🔴" if state.rpm  >= 6500 else ("🟡" if state.rpm  >= 5000 else "🟢")
    fuel_icon = "⛽🔴" if state.fuel <= 15   else "⛽"
    temp_icon = "🌡️🔴" if state.oil_temp >= 110 else ("🌡️🟡" if state.oil_temp >= 90 else "🌡️🟢")
    ce_icon   = " ⚠️ CHECK ENGINE" if state.check_engine else ""

    faults_tag = f" | Falhas: {len(state.faults)}" if state.faults else ""
    shifting_tag = "AGUARDE" if state.shifting else "  "

    print(
        f"\r"
        f"[{state.gear:>2}]{shifting_tag} "
        f"RPM:{state.rpm:>5.0f}{rpm_icon}{rpm_bar} "
        f"Vel:{state.speed:>6.1f}km/h {spd_bar} "
        f"{fuel_icon}{state.fuel:>5.1f}% {fuel_bar} "
        f"Auto:{state.autonomy:>5.0f}km "
        f"{temp_icon}{state.oil_temp:>5.1f}°C {temp_bar}"
        f"{ce_icon}{faults_tag}   ",
        end=""
    )


def _print_fault_commands():
    """Exibe os comandos de teste de falhas disponíveis."""
    print("\nFalhas disponíveis para teste (ative via código):")
    print("   faults.activate('sensor_rpm')        → Falha no sensor de RPM")
    print("   faults.activate('sensor_speed')      → Falha no velocímetro")
    print("   faults.activate('sensor_fuel')       → Falha no sensor de combustível")
    print("   faults.activate('engine_overheat')   → Superaquecimento")
    print("   faults.activate('engine_misfire')    → Falha de ignição")
    print("   faults.activate('brake_failure')     → Falha no freio")
    print("   faults.activate('fuel_leak')         → Vazamento de combustível")
    print("   faults.activate('transmission_fault')→ Câmbio travado")
    print("   (Sprint 9 terá a tela de controle visual!)\n")


def _build_bar(value, min_val, max_val, length=10):
    ratio = (value - min_val) / (max_val - min_val)
    ratio = max(0.0, min(ratio, 1.0))
    filled = int(ratio * length)
    return "[" + "█" * filled + "░" * (length - filled) + "]"