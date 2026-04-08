import pygame

class ControllerInput:
    """
    Captura entradas do controle ou simulador de corrida
    Usa pygame para leitura dos eixos e botoes em tempo real
    """

    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.joystick = None
        self._connect()

    def _connect(self):
        """Tenta conectar ao primeiro controle encontrado."""
        count = pygame.joystick.get_count()

        if count == 0:
            print("Nenhum controle detectado. Rodando sem input físico.")
            return

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        print(f"Controle conectado: {self.joystick.get_name()}")

    def is_connected(self):
        return self.joystick is not None

    def _get_trigger(self, axis_id):
        """Converte eixo do gatlho (-1 <-> +1) para 0.0<->1.0"""
        if not self.is_connected():
            return 0.0
        raw = self.joystick.get_axis(axis_id)
        return (raw + 1.0) / 2.0

    def get_throttle(self):
        return self._get_trigger(5) # RT

    def get_brake(self):
        return self._get_trigger(4) #LT

    def get_gear_shift(self):
        """
        Retorna +1 (RB), -1 (LB) ou 0.
        Processa eventos pygame para detectar o momento exato do pressionamento.
        """
        if not self.is_connected():
            return 0

        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 5:   # RB
                    return 1
                elif event.button == 4: # LB
                    return -1

        return 0

    def update(self, state, gearbox):
        """
        Lê todos os inputs e atualiza o CarState.
        Chamado a cada tick do loop principal.
        """
        # Atualiza acelerador e freio
        state.throttle = self.get_throttle()
        state.brake = self.get_brake()

        # Atualiza marcha
        shift = self.get_gear_shift()
        if shift != 0:
            gearbox.request_shift(state, shift)

    def quit(self):
        pygame.quit()