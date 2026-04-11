import tkinter as tk
from engine.car_state import CarState
from core.loop import start_simulation_thread
from dashboard.panel import Dashboard


def main():
    print("=" * 50)
    print("  InnovaAuto — Iniciando...")
    print("=" * 50)

    # Estado compartilhado entre simulação e UI
    state = CarState()

    # Inicia simulação em thread separada
    start_simulation_thread(state)

    # Inicia interface gráfica na thread principal
    root = tk.Tk()
    dashboard = Dashboard(root, state)

    # Ao fechar a janela, encerra a simulação também
    def on_close():
        state.running = False
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()