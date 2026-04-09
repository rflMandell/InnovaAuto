# essa parte tem chances muito altas de eu errar, entao pfv papai do ceu seja piedoso com seu filho

#rpm de idle (ligado mas sem acelerar)
RPM_IDLE = 800.

# RPM de redline (core de giro)
RPM_REDLINE = 7000.0 # valor aceitavel pra carro popular (eu acho)

#Rpm durante a troca de marcha (cai um tico)
RPM_SHIFTING = 1200.0

#Velocidade de subida de RPM por tick (quando sobe ao acelerar)
RPM_RISE_RATE = 4500.0 #RPM por segundo (sim, rotacoes por miouto contadas por segundo :3)

#velocidade de queda de RPM por tick
RPM_FALL_RATE = 2500.0 

#limite maximo de RPM por marcha
RPM_LIMIT_PER_GEAR = {
    'R': 4000.0,
    'N': 3000.0,
    '1': 7000.0,
    '2': 7000.0,
    '3': 7000.0,
    '4': 7000.0,
    '5': 7000.0,
}


class Motor:
    """
    Simula o comportamento do motor, subida e queda de RPM,
    idle, redline e corte de giro.
    """
    
    def update(self, state, delta_time):
        """
        Atualiza o RPM no CARState e cada tick
        
        delta_time: tempo em segundos desde o ultimo tick
        """
        
        # durante a troca de marcha, RPM cai para simular engate
        if state.shifting:
            state.rpm = _approach(
                current=state.rpm,
                target=RPM_SHIFTING,
                rate=RPM_FALL_RATE,
                delta=delta_time
            )
            return
        
        #pega o limite de RPM da marcha atual
        gear_limit = RPM_LIMIT_PER_GEAR.get(state.gear, RPM_REDLINE)
        
        #calcula o RPM alvo baseado no acelerador
        throttle = state.throttle
        
        if throttle > 0.01:
            #acelrando, RPM sobe em direcao ao limite da marcha
            target_rpm = RPM_IDLE + (gear_limit - RPM_IDLE) * throttle
            state.rpm = _approach(
                current=state.rpm,
                target=target_rpm,
                rate=RPM_RISE_RATE,
                delta=delta_time
            )
        else:
            #sem acelerador RPM cai em direcao ao idle
            state.rpm = _approach(
                current=state.rpm,
                target=RPM_IDLE,
                rate=RPM_FALL_RATE,
                delta=delta_time
            )
            
        #aplica corte de giro se ultrapassar o redline
        if state.rpm > RPM_REDLINE:
            state.rpm = RPM_REDLINE
            _redline_cut(state)
            
        #garante q rpm nunca vai abaixo do idle
        if state.rpm < RPM_IDLE:
            state.rpm = RPM_IDLE
            
            
def _approach():
    """
    Move 'current' em direcao a 'target' na velocidade 'rate' por segundo.
    n ultrapassa o target
    """
    

def _redline_cur(state):
    """
    a
    """