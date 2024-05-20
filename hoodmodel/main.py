#! /usr/bin/env python3
# ---------------------------------
# Author: Erwan DAVID
# Year: 2021
# Lab: SGL, Goethe University, Frankfurt
# Comment: 
# ---------------------------------


import os
from glob import glob
from pathlib import Path

# pip install ffmpeg-python
import ffmpeg

# pip install moderngl-window
import moderngl_window as mglw
from moderngl_window import resources as mlgw_resources
from moderngl_window.conf import settings as mlgw_settings

from Renderer import Renderer

DATA_INPUTS = "./indata/"
DATA_OUTPUTS = "./outdata/"
DATA_OUTTMP = "./outdata/tmp/"

Renderer.outdir = DATA_OUTTMP

os.makedirs(DATA_INPUTS+"Textures", exist_ok=True)
os.makedirs(DATA_OUTPUTS, exist_ok=True)
os.makedirs(DATA_OUTTMP, exist_ok=True)

# Clear file
open("failed", "w").close()

for obj_path in glob(DATA_INPUTS + "/*.obj"):

	print(obj_path)

	obj_file = obj_path.split(os.sep)[-1]
	obj_folder = os.sep.join(obj_path.split(os.sep)[:-1]) + os.sep

	obj_basename = os.path.basename(obj_file)

	out_anim = f"{DATA_OUTPUTS}{obj_basename[:-4]}.webm"

	generate_visuals = not os.path.isfile(f"{DATA_OUTPUTS}{obj_basename[:-4]}.jpg")
	
	# generate_visuals = True
	if not generate_visuals:
		# print(f"{out_anim} exists")
		# exit()
		continue

	print(obj_file)

	Renderer.reset()

	mlgw_settings.TEXTURE_DIRS = []
	mlgw_settings.SCENE_DIRS = []
	mlgw_settings.DATA_DIRS = []

	# mlgw_resources.register_dir(Path(obj_folder))

	Renderer.resource_dir = Path(obj_folder)
	Renderer.obj_path = obj_basename
	Renderer.out_dir = DATA_OUTTMP
	Renderer.no_render = not generate_visuals
	# exit()

	if generate_visuals:
		
		print("=" * 20)

		try:
			mglw.run_window_config(Renderer,
				# args=["-wnd", "headless"]
				# args=["-wnd", "pyqt5"]
				)

			Renderer.instance.ctx.release()
			Renderer.instance.wnd.close()

		except Exception as e:
			print("  FAILED:")
			print("\t", e)

			Renderer.instance.ctx.release()
			Renderer.instance.wnd.close()

			with open("failed", "a") as f:
				f.write(f"{obj_file}\n")
				f.write(f"\t{e}\n")

			continue
	else:
		continue
		Renderer.load_sceneOver(Renderer.obj_path)

	# ffmpeg -framerate 24 -pix_fmt rgb8 -i ./outdata/tmp/output%03d.jpg
	stream = ffmpeg.input(f"./{DATA_OUTTMP}/output%03d.jpg", framerate=24, pixel_format="rgb8")
	stream = ffmpeg.output(stream, out_anim)
	stream = ffmpeg.overwrite_output(stream)
	ffmpeg.run(stream)

	os.rename(f"./{DATA_OUTTMP}/output001.jpg", f"{DATA_OUTPUTS}{obj_basename[:-4]}.jpg")