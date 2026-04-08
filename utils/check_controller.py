import pygame
import time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Nenhum controle detectado")
    exit()
    
js = pygame.joystick.Joystick(0)
js.init()
print(f"Controle: {js.get_name()}")
print(f"Eixos: {js.get_numaxes()} | botos: {js.get_numbuttons()}")
print("\nMexa nos gatilhos e botos para ver os valores:\n")

try:
    while True:
        pygame.event.pump()
        eixos = [round(js.get_axis(i), 2) for i in range(js.get_numaxes())]
        botoes = [js.get_button(i) for i in range(js.get_numbuttons())]
        print(f"\rEixos: {eixos} | botoes {botoes} ", end="")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nEncerrado")
    pygame.quit()