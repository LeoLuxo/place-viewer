import os, sys, subprocess

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
os.environ['SDL_VIDEO_CENTERED'] = "1"
subprocess.call("", shell=True)

import glob
from datetime import datetime
from time import time as now
from math import copysign
from zipfile import ZipFile

import pygame
from pygame import display, Rect, Color, Surface
import pygame.freetype

from settings import *

gen = (len(sys.argv) >= 2 and sys.argv[1].startswith("gen")) or not os.path.isdir("img_cache")

COLORS = ["0xFFFFFF", "0xE4E4E4", "0x888888", "0x222222", "0xFFA7D1", "0xE50000", "0xE59500", "0xA06A42", "0xE5D900", "0x94E044", "0x02BE01", "0x00E5F0", "0x0083C7", "0x0000EA", "0xE04AFF", "0x820080"]

S = 1000
BIG_OFFSET = 100
SML_OFFSET = 20
BIG_LEN = 16559897
TIME_START = 1490918688
TIME_END = 1491238734
GEN_TIME_INC = 4900
LINE_BYTES = 25
BEGINNING = 1490979600

tickrate = 60
speed = 1000
time = TIME_START
pause = True
zoom = (0, 0, S, S)
zoom_select = None
safety = now()

pygame.init()

screen = display.set_mode((W + 2*SML_OFFSET, H + BIG_OFFSET + SML_OFFSET))
display.set_caption("r/place viewer")
display.set_icon(pygame.image.load("assets/place.png"))
clock = pygame.time.Clock()

font = pygame.freetype.Font("assets/PressStart2P.ttf", 24)

screen.fill((200, 200, 200))
font.render_to(screen, (10, 10), "Loading...", (0, 0, 0))
display.flip()

draw_surf = Surface((S, S))
draw_surf.fill((0, 0, 0))

def seek(st):
	global draw_surf, cache, data_file, time
	
	safe_t = now()
	
	time = max(TIME_START, min(TIME_END, st))
	
	# print(f"Seeking to: {int(time)} seconds")
	
	nearest = TIME_START
	for k in cache.keys():
		if k > nearest and k <= time:
			nearest = k
	
	draw_surf.blit(cache[nearest][0], (0, 0))
	data_file.seek(LINE_BYTES * cache[nearest][1])
	
	draw()

def draw():
	global draw_surf, data_file, time, zoom
	
	i = 0
	while True:
		i += 1
		l = data_file.readline()
		if l == None or l == "":
			break
		
		t, x, y, c = [int(e) for e in l.strip("\n").split(",")]
		
		if t > time:
			break
		elif zoom[0] <= x < zoom[0]+zoom[2] and zoom[1] <= y < zoom[1]+zoom[3] and 0 <= c < len(COLORS):
			draw_surf.set_at((x, y), Color(COLORS[c]))


if gen:
	gen_surf = Surface((W, H))
	gen_surf.fill((0, 0, 0))
	
	print("Unzipping data...")
	with ZipFile('full_data.zip', 'r') as data:
		data.extractall()
	
	print("Clearing image cache...")
	if not os.path.isdir("img_cache"):
		os.mkdir("img_cache")
	
	files = glob.glob("img_cache/*.png")
	for f in files:
		os.remove(f)
	
	print("Generating image cache...\n")
	with open("full_data.txt", "r") as f:
		t_inc = GEN_TIME_INC
		
		pygame.image.save(gen_surf, f"img_cache/{TIME_START}-0.png")
		
		for i, raw in enumerate(f):
			t, x, y, c = [int(e) for e in raw.strip("\n").split(",")]
			
			dt = t - TIME_START
			
			if dt > t_inc:
				pygame.image.save(gen_surf, f"img_cache/{t}-{i}.png")
				t_inc += GEN_TIME_INC
			
			if 0 <= x < W and 0 <= y < H and 0 <= c < len(COLORS): 
				gen_surf.set_at((x, y), Color(COLORS[c]))
			
			if i % 20000 == 0:
				print(f"\033[1F   {i / BIG_LEN * 100:.2f}%")
				
				if pygame.event.peek(eventtype=pygame.QUIT):
					sys.exit()
		
		pygame.image.save(gen_surf, f"img_cache/{TIME_END}-{BIG_LEN-1}.png")
	
	print(f"\033[1F   Done.     ")


print("Building cache...\n")
cache = {}
cache_files = glob.glob("img_cache/*.png")
for i, f in enumerate(cache_files):
	name = f.strip("img_cache\\.png").split("-")
	cache.update({int(name[0]) : (pygame.image.load(f).convert(), int(name[1]))})
	print(f"\033[1F   {i / len(cache_files) * 100:.1f}%")
	if pygame.event.peek(eventtype=pygame.QUIT):
		sys.exit()
print(f"\033[1F   Done.     ")


data_file = open("full_data.txt", "r")

print("Starting display")
seek(BEGINNING)

pygame.event.clear()

exit = False
while not exit:
	for e in pygame.event.get():
		if e.type == pygame.QUIT:
			exit = True
		if e.type == pygame.KEYDOWN:
			if e.key == pygame.K_RIGHT:
				if pygame.key.get_pressed()[pygame.K_LSHIFT]:
					seek(int(time + SHORT_JUMP))
				else:
					seek(int(time + BIG_JUMP))
			elif e.key == pygame.K_LEFT:
				if pygame.key.get_pressed()[pygame.K_LSHIFT]:
					seek(int(time - SHORT_JUMP))
				else:
					seek(int(time - BIG_JUMP))
			if e.key == pygame.K_UP:
				speed = SPEEDS[min(len(SPEEDS)-1, SPEEDS.index(speed) + 1)]
			elif e.key == pygame.K_DOWN:
				speed = SPEEDS[max(0, SPEEDS.index(speed) - 1)]
			elif e.key == pygame.K_SPACE:
				pause = not pause
		if e.type == pygame.MOUSEBUTTONDOWN:
			if e.button == 3:
				zoom = (0, 0, S, S)
				seek(time)
	
	if time >= TIME_END:
		pause = True
		time = TIME_END
	
	if SAFE_FPS and clock.get_fps() / tickrate <= 0.7 and now() - safety >= 0.3 and not pause:
		speed = SPEEDS[max(0, SPEEDS.index(speed) - 1)]
		safety = now()
	
	if pygame.mouse.get_pressed()[0]:
		mx, my = pygame.mouse.get_pos()
		x, y = mx - SML_OFFSET, my - BIG_OFFSET
		if zoom_select == None:
			zoom_select = (min(W-1, max(0, x)), min(H-1, max(0, y)), 0, 0)
		else:
			mx = max(-zoom_select[0], min(W-1 - zoom_select[0], x - zoom_select[0]))
			my = max(-zoom_select[1], min(H-1 - zoom_select[1], y - zoom_select[1]))
			if copysign(-1, mx) == copysign(-1, my):
				zoom_select = (zoom_select[0], zoom_select[1], min(mx, my, key=abs), min(mx, my, key=abs))
			else:
				zoom_select = (zoom_select[0], zoom_select[1], min(mx, -my, key=abs), min(-mx, my, key=abs))
	elif zoom_select != None:
		zoom = (int(zoom_select[0] / W * zoom[2] + zoom[0]), int(zoom_select[1] / H * zoom[3] + zoom[1]), int(zoom_select[2] / W * zoom[2]), int(zoom_select[3] / H * zoom[3]))
		if zoom[2] < 0:
			zoom = (zoom[0] + zoom[2], zoom[1], abs(zoom[2]), zoom[3])
		if zoom[3] < 0:
			zoom = (zoom[0], zoom[1] + zoom[3], zoom[2], abs(zoom[3]))
		zoom_select = None
	
	screen.fill((200, 200, 200))
	
	font.render_to(screen, (10, 10), f"{'-' if pause else '>'} {speed}x", (0, 0, 0))
	font.render_to(screen, (10, 60), f"{int(clock.get_fps())} fps", (0, 255, 0) if clock.get_fps() / tickrate > 0.9 else ((255, 255, 0) if clock.get_fps() / tickrate > 0.7 else (255, 0, 0)))
	font.render_to(screen, (W+2*SML_OFFSET - font.get_rect(f"{int(time)}")[2] - 10, 10), None, (0, 0, 0))
	font.render_to(screen, (W+2*SML_OFFSET - font.get_rect(datetime.fromtimestamp(time).strftime("%d/%m/%y %H:%M:%S"))[2] - 10, 60), None, (0, 0, 0))
	
	draw()
	cropped = Surface(zoom[2:])
	cropped.blit(draw_surf, (0, 0), zoom)
	screen.blit(pygame.transform.scale(cropped, (W, H)), (SML_OFFSET, BIG_OFFSET))
	
	if zoom_select != None:
		pygame.draw.rect(screen, (255, 255, 255), Rect(zoom_select[0] + SML_OFFSET, zoom_select[1] + BIG_OFFSET, zoom_select[2], zoom_select[3]), 5)
		pygame.draw.rect(screen, (0, 0, 0), Rect(zoom_select[0] + SML_OFFSET, zoom_select[1] + BIG_OFFSET, zoom_select[2], zoom_select[3]), 3)
		
	display.flip()
	clock.tick(tickrate)
	
	if not pause:
		time += clock.get_time() / 1000 * speed

data_file.close()
