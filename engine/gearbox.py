import time

GEAR_SEQUENCE = ['R', 'N', '1', '2', '3', '4', '5']
GEAR_SHIFT_DELAY = 0.4
MAX_RPM_FOR_REVERSE = 800


class Gearbox:
    """
    Sistema de câmbio do InnovaAuto.
    Agora respeita falha de transmissão do FaultManager.
    """

    def __init__(self):
        self._last_shift_time = 0.0
        self._shift_complete_time = 0.0
        self.fault_manager = None   # depois eu resolvo isso da melhor maneira mas por enquanto fica assim

    def can_shift(self):
        return (time.time() - self._last_shift_time) >= GEAR_SHIFT_DELAY

    def request_shift(self, state, direction):
        # Bloqueia se câmbio travado por falha
        if self.fault_manager and self.fault_manager.is_active('transmission_fault'):
            print(f"\n  Câmbio travado por falha de transmissão!")
            return False

        if not self.can_shift():
            return False

        current = state.gear
        if current not in GEAR_SEQUENCE:
            current = 'N'

        current_index = GEAR_SEQUENCE.index(current)
        new_index = current_index + direction

        if new_index < 0 or new_index >= len(GEAR_SEQUENCE):
            print(f"\n  Limite de marcha atingido ({current})")
            return False

        new_gear = GEAR_SEQUENCE[new_index]

        if new_gear == 'R' and state.speed > 2.0:
            print(f"\n  Não é possível engatar ré com o carro em movimento!")
            return False

        if current == 'R' and new_gear == '1':
            print(f"\n  Passe pelo neutro antes de engatar 1ª")
            return False

        if direction == -1 and state.rpm > 4000 and new_gear not in ('N',):
            print(f"\n  RPM alto demais para descer marcha ({state.rpm:.0f} RPM)")
            return False

        old_gear = state.gear
        state.gear = new_gear
        state.shifting = True
        self._last_shift_time = time.time()
        self._shift_complete_time = time.time() + GEAR_SHIFT_DELAY
        print(f"\n  Marcha: {old_gear} → {state.gear}")
        return True

    def update(self, state):
        if state.shifting:
            if time.time() >= self._shift_complete_time:
                state.shifting = False