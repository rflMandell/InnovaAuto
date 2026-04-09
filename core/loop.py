import time
from engine.car_state import CarState
from engine.gearbox import Gearbox
from engine.motor import Motor
from input.controller import ControllerInput

TICK_RATE = 5

def run():
    state = CarState()
    controller = ControllerInput()
    gearbox = Gearbox()
    motor = Motor()
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

            # Exibe estado atual no terminal
            rpm_bar = _rpm_bar(state.rpm)
            shifting_tag = " Aguarde" if state.shifting else ""
            print(
                f"\r[Marcha: {state.gear:>2} {shifting_tag}] "
                f"RPM: {state.rpm:>6.0f} {rpm_bar} | "
                f"Acelerador: {state.throttle:.2f} | "
                f"Freio: {state.brake:.2f}",
                end=""
            )

            #controla o tempo para manter o tick constante
            elapsed = time.time() - now
            sleep_time = tick_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n\nSistema encerrado.")
    finally:
        controller.quit()
        
def _rpm_bar(rpm, max_rpm=7000, bar_length=20):
    """Exibe uma barra visual de RPM no terminal."""
    filled = int((rpm / max_rpm) * bar_length)
    filled = max(0, min(filled, bar_length))
    bar = "█" * filled + "░" * (bar_length - filled)
    #mudar o simbolo perto do redline
    if rpm >= 6500:
        return f"[{bar}] 🔴"
    elif rpm >= 5000:
        return f"[{bar}] 🟡"
    else:
        return f"[{bar}] 🟢"