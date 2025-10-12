import pygame

def init():
    pygame.init()
    screen = pygame.display.set_mode((400, 400))

def get_key(key_name):
    ans = False
    for _ in pygame.event.get(): pass
    key_input = pygame.key.get_pressed()
    formatted_key = getattr(pygame, f"K_{key_name}")
    if key_input[formatted_key]:
        ans = True
    pygame.display.update()
    return ans


if __name__ == "__main__":
    screen = init()
    while True:
        if get_key("LEFT"):
            print("Left key is pressed")
        elif get_key("RIGHT"):
            print("Right key is pressed")