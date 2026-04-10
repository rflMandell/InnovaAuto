# o loopzao louco q faz a porra toda funcionar
import time
from engine.car_state import CarState
from engine.gearbox import Gearbox
from engine.motor import Motor
from engine.velocity import Velocity
from input.controller import ControllerInput

TICK_RATE = 5

def run():
    state = CarState()
    controller = ControllerInput()
    gearbox = Gearbox()
    motor = Motor()
    velocity = Velocity()
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
    rpm_bar = _build_bar(state.rpm, 0, 7000, length=15)
    spd_bar = _build_bar(state.speed, 0, 220, length=15)
    shifting_tag = " Aguardando" if state.shifting else "   "

    #mudar o simbolo perto do redline
    if state.rpm >= 6500:
        rpm_icon = "🔴"
    elif state.rpm >= 5000:
        rpm_icon = "🟡"
    else:
        rpm_icon = "🟢"
        
    print(
        f"\r"
        f"Marcha: {state.gear:>2} {shifting_tag} | "
        f"RPM: {state.rpm:>5.0f} {rpm_icon} {rpm_bar} | "
        f"Vel: {state.speed:>6.1f}km/h {spd_bar} | "
        f"Acel: {state.throttle:.2f} | "
        f"Freio: {state.brake:.2f}",
        end=""
    )
        
def _build_bar(value, min_val, max_val, length=15):
    """Gera uma barra de progresso visual para o terminal"""
    ratio = (value - min_val) / (max_val - min_val)
    ratio = max(0.0, min(ratio, 1.0))
    filled = int(ratio* length)
    return "[" + "█" * filled + "░" * (length - filled) + "]"