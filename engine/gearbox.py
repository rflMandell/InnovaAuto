import time

#sequencia valida de marchas
GEAR_SEQUENCE = ['R', 'N', '1', '2', '3', '4', '5']

# tempo minimo entre trocas - para simular delay mecanico
GEAR_SHIFT_DELAY = 0.4

#rpm maximo permitido para engatar marcha R ou N (questao de seguranca)
MAX_PRM_FOR_REVERSE = 800

class Gearbox:
    """
    Sistema de cambio do InnovaAuto.
    Controle a logica de troca de marchas com validacoes e delay "realista"
    """
    
    def __init__(self):
        self._last_shift_time = 0.0
        self._shiftinhg = False 
        self._shift_complete_time = 0.0
        
    def can_shift(self):
        """Verifica se ja passou o delay desde a ultima troca"""
        return (time.time() - self._last_shift_time) >= GEAR_SHIFT_DELAY
    
    def request_shift(self, state, direction):
        """
        Tenta trocar a marcha.
        
        direction: +1 para subir, -1 para descer
        
        Returns:
            True -> caso troca for aceite / False -> caso for bloqueada
        """
        
        #block se ainda esta no delay da troca anterior
        if not self.can_shift():
            return False
        
        current = state.gear
        if current not in GEAR_SEQUENCE:
            current = 'N'
            
        current_index = GEAR_SEQUENCE.index(current)
        new_index = current_index + direction
        
        #block se ja esta no extremo da sequence
        if new_index < 0 or new_index >= len(GEAR_SEQUENCE):
            print(f"\nLimite de marcha atigindo ({current})")
            return False
        
        new_gear = GEAR_SEQUENCE[new_index]
        
        #validacao de seugranca: nao engatar R com carro em movimento
        if new_gear == 'R' and state.speed > 2.0:
            print(f"\nNao e possivel engatar re com o carro em movimento ({state.speed:.1f}km/h)")
            return False
        
        #validacao de seguranda: nao sai de R para 1 sem passar por N
        if current == 'R' and new_gear == '1':
            print(f"\nPasse pelo neutro antes de engatar 1")
            return False
        
        #validacao: RPM muito alto para descer marcha bruscamente
        if direction == -1 and state.rpm > 4000 and new_gear not in ('N',):
            print(f"\nRPM alto demais para descer marcha ({state.rpm:.0f} RPM)")
            return False
        
        #troca aceita
        old_gear = state.gear
        state.gear = new_gear
        state.shifting = True
        self._last_shift_time = time.time()
        self._shift_complete_time = time.time() + GEAR_SHIFT_DELAY
        
        print(f"\n Marcha: {old_gear} ->  {state.gear}")
        return True
    
    def update(self, state):
        """
        Chamado a cada tick
        Gerencia o estado de 'shifting' (durante troca)
        """
        if state.shifting:
            if time.time() >= self._shift_complete_time:
                state.shifting = False #troca concluida