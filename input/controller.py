import pygame

class ControllerInput:
    """
    Captura entradas do controle ou simulador de corrida
    Usa pygame para leitura dos eixos e botoes em tempo real
    """
    def __init__(self):
        # inicializa apeans o modulo de joystick do pygame
        pygame.init()
        pygame.joystick.init()
        self.joystick = None
        self._gear_cooldown = 0 #evitar troca de marchar multuplas
        self.connect()
    
    def connect(self):
        """Tenta conectar ao primeiro controle encontrado."""
        count = pygame.joystick.get_count()
        if count == 0:
            print("Nenhum controle detectado. Todando input fisico")
            return
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        print(f"Controle conectado: {self.joystick.get_name()}")
    
    def is_conected(self):
        return self.joystick is not None
    
    def _get_trigger(self, axis_id):
        """
        Gatilhos do Xbox retornam -1.0 a +1.0.
        Converte para 0.0 a 1.0.
        """
        if not self.is_conected():
            return 0.0
        raw = self.joystick.get_axis(axis_id)
        return (raw + 1.0) / 2.0 #normaliza para 0.0 <-> 1.0
    
    def get_throttle(self):
        """RT = eixo 5 (pode variar por OS, se precisar reconfigurar a depender de qual maquina usar pra codar e testar)"""
        return self._get_trigger(5)
    
    def get_brake(self):
        """LT = eixo 4"""
        return self._get_trigger(4)
    
    def get_gear_shift(self):
        """
        Returns:
            +1 se RB foi pressionado (para subir a marcha)
            -1 se LB foi pressionado (para descer a marcha)
            0 se nenhum botao de marcha foi pressionado
        """
        if not self.is_conected():
            return 0
        #processa eventos do pygame para detectar KEYDOWN dos botoes
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 5: #RB
                    return 1
                elif event.button == 4: #LB
                    return -1
        return 0
    def update(self, state):
        """
        Le todos os inputs e att o CarState.
        Chamado a cada tick do loop principal
        """
        #att acelerador e freio
        state.throttle = self.get_throttle
        state.brake = self.get_brake()
        #atualizar a marcha atual
        shift = self.get_gear_shift()
        if shift != 0:
            _apply_gear_shift(state, shift)
    def quit(self):
        """Encerra o pygame"""
        pygame.quit()
        
#sequencia de marchas
GEAR_SEQUENCE = ['R', 'N', '1', '2', '3', '4', '5']
def _apply_gear_shift(state, direction):
    """
    Aplica a troca de marcha baseado na direcao (+1 sobre, -1 desce)
    Respeita os limites da sequencia
    """
    current = state.gear
    if current not in GEAR_SEQUENCE:
        current = 'N'
    current_index = GEAR_SEQUENCE.index(current)
    new_index = current_index + direction
    #limite aos extremos da lista
    new_index = max(0, min(new_index, len(GEAR_SEQUENCE) - 1))
    old_gear = state.gear
    state.gear = GEAR_SEQUENCE[new_index]
    if old_gear != state.gear:
        print(f"Marcha: {old_gear} -> {state.gear}")