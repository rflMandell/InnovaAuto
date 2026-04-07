import time
from engine.car_state import CarState

TICK_RATE = 5 #30aps

def run():
    """
    Loop principal do InnovaAuto
    Atualiza o estado do carro continuamente ate o user encerrar o programa
    """
    state = CarState()
    tick_interval = 1.0 / TICK_RATE
    print("=" * 50)
    print("InnovaAuto - Sistema Iniciado")
    print(f"Tick Rate: {TICK_RATE}/s | Pressione Ctrl+C para sair")
    print("=" * 50)
    try:
        while state.running:
            start_time = time.time()
            # aqui entrarao as chamadas dos outros modulos quando eu fazer eles pq nao estao feito :3
            print(state)
            #controla o tempo para manter o tick constante
            elapsed = time.time() - start_time
            sleep_time = tick_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        print("\n\nSistema encerrado.")