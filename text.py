
from resources import *
import pygame

offset = 0
text_to_render = []


def prep_font(resources):
    font = pygame.font.Font(None, 16)  # 16 pt font
    resources["font"] = font


def render_text(text, color=(0, 0, 0)):
    global offset
    global text_to_render
    font = get_resource("font")
    size = font.size(text)
    h = size[1]
    size = pygame.Rect((0, offset), size)
    offset += h
    text = font.render(text, False, color)
    text_to_render.append((text, size))


def clear_text_buffer():
    global offset
    global text_to_render
    offset = 0
    text_to_render = []
