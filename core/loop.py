import time
from engine.car_state import CarState
from engine.gearbox import Gearbox
from input.controller import ControllerInput

TICK_RATE = 5

def run():
    state = CarState()
    controller = ControllerInput()
    gearbox = Gearbox()
    tick_interval = 1.0 / TICK_RATE

    print("=" * 50)
    print("InnovaAuto - Sistema Iniciado")
    print(f"Tick rate: {TICK_RATE}/s | Pressione Ctrl+C para sair")
    print("=" * 50)

    try:
        while state.running:
            start_time = time.time()

            # -- Leitura do controle --
            controller.update(state, gearbox)
            gearbox.update(state)

            # Exibe estado atual no terminal
            shifting_tag = " Aguarde" if state.shifting else ""
            print(
                f"\r[Marcha: {state.gear:>2}{shifting_tag}] "
                f"Acelerador: {state.throttle:.2f} | "
                f"Freio: {state.brake:.2f}",
                end=""
            )

            #controla o tempo para manter o tick constante
            elapsed = time.time() - start_time
            sleep_time = tick_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n\nSistema encerrado.")
    finally:
        controller.quit()