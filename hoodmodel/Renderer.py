#! /usr/bin/env python3
# ---------------------------------
# Author: Erwan DAVID
# Year: 2021
# Lab: SGL, Goethe University, Frankfurt
# Comment:
# ---------------------------------

from PIL import Image
import numpy as np

# pip install pyrr
from pyrr import Matrix44
# pip install pywavefront
import pywavefront
# pip install PyOpenGL
import OpenGL.GL as gl
from OpenGL.GL import *

import moderngl
import moderngl_window as mglw
# from moderngl_window import screenshot
from moderngl_window.scene.camera import OrbitCamera

RENDER_SIZE = (256, 256) # Web visualisation 
RENDER_SIZE = (320, 320) # Object placement visualisation
RENDER_SIZE = (512, 512) # Object placement visualisation ++
# RENDER_SIZE = (128, 128) # TESTING

class Renderer(mglw.WindowConfig):

	window_size = RENDER_SIZE
	aspect_ratio = RENDER_SIZE[0] / RENDER_SIZE[1]
	resizable = False
	clear_color = 1,1,1, 1
	log_level = None
	
	# Headless does not like that setting
	samples = 8

	resource_dir = None
	title = "3D renderer"
	out_dir = "./"
	obj_path = None
	store_image = False

	instance = None

	def __init__(self, **kwargs):

		super().__init__(**kwargs)

		Renderer.instance = self

		self.wnd._window.minimize()

		self.obj_file = Renderer.obj_path


		self.prog = self.ctx.program(
			vertex_shader='''
				#version 330
				uniform mat4 Mvp;

				in vec3 in_position;
				in vec3 in_normal;
				in vec2 in_texcoord_0;
				out vec3 v_vert;
				out vec3 v_norm;
				// out vec2 v_text;
				void main() {
					gl_Position = Mvp * vec4(in_position, 1.0);
					v_vert = in_position;
					v_norm = in_normal;
				}
			''',
			fragment_shader='''
				#version 330
				uniform vec3 Light;
				uniform vec3 Color;
				uniform sampler2D Texture;

				in vec3 v_vert;
				in vec3 v_norm;
				in vec2 v_text;
				out vec4 f_color;
				void main() {
					float lum = clamp(dot(normalize(Light - v_vert), normalize(v_norm)), 0.0, 1.0) * 1 + 0.1;
					f_color = vec4(Color * lum, 1.0);
				}
			'''
			)

		self.mvp = self.prog['Mvp']
		self.light = self.prog['Light']
		self.color = self.prog['Color']
		# self.use_texture = self.prog['UseTexture']

		target, radius, far_cam = Renderer.load_sceneOver(self.obj_file)

		self.camera = OrbitCamera(aspect_ratio=self.wnd.aspect_ratio,
			target=target,
			radius=radius,
			near=.001,
			far=far_cam)

		self.camera_enabled = True
		self.scene = self.load_scene(self.obj_file)

		self.vaos_scene = [ node.mesh.vao.instance(self.prog) for node in self.scene.root_nodes ]

		# print(self.scene.root_nodes[0].mesh.mesh_program.program._members.items())

		# print(self.scene.materials[0].color)
		# exit()

		self.iscreenshot = 0
		self.nscreenshot = 100

		self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
		
		# print(self.resource_dir, self.obj_file)

	def reset():
		Renderer.sceneA = None
		Renderer.obj_path = None
		Renderer.resource_dir = None
		Renderer.out_dir = None
		Renderer.no_render = None

	def load_sceneOver(obj_file):
		# Compute Object bbox ##########
		scene = pywavefront.Wavefront(Renderer.resource_dir / obj_file, collect_faces=True)

		# print(Renderer.resource_dir, obj_file)

		scene_box = (scene.vertices[0], scene.vertices[0])
		for vertex in scene.vertices:
			min_v = [min(scene_box[0][i], vertex[i]) for i in range(3)]
			max_v = [max(scene_box[1][i], vertex[i]) for i in range(3)]
			scene_box = (min_v, max_v)
		scene_box = list(map(np.array, scene_box))

		Renderer.sceneA = scene

		scene_mat = []
		scene_tex = []

		for mesh in scene.mesh_list:
			for mat in mesh.materials:

				if mat.name not in scene_mat:
					scene_mat.append(mat.name)

				for el in dir(mat):
					if el.split("_")[0] != "texture": continue
					if el == "texture_cls": continue

					tex = getattr(scene.mesh_list[0].materials[0], el)

					if tex is not None:

						if tex.file_name not in scene_tex:
							scene_tex.append(tex.file_name)

		setattr(Renderer.sceneA, "scene_mat", scene_mat)
		setattr(Renderer.sceneA, "scene_tex", scene_tex)
		setattr(Renderer.sceneA, "scene_box", scene_box)

		# print(scene_box)
		# Affects
		#	camera "target"
		target = (scene.scene_box[0]+scene.scene_box[1])/2
		#	camera "radius" - we suppose that the object is centered on 0,0,0
		radius = max(np.abs(scene.scene_box[0]-scene.scene_box[1])) * 1.5
		#	camera "far"
		far_cam = radius * 1000
		###############################
		# print(target)
		# print(radius)
		# print(far_cam)

		return target, radius, far_cam

	def render(self, time: float, frametime: float):

		if Renderer.no_render:
			self.wnd.close()
			return

		self.ctx.clear(*Renderer.clear_color)
		self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

		self.camera.angle_x += 360 / self.nscreenshot
		
		translation = Matrix44.from_translation((0, 0, 0))
		rotation = Matrix44.from_eulers((0, 0, 0))
		model_matrix = translation * rotation
		camera_matrix = self.camera.matrix * model_matrix

		renderManual = False
		# renderManual = True # For when texture rendering fails
		if renderManual:

			self.mvp.write( (self.camera.projection.matrix * camera_matrix).astype('f4'))

			self.light.value = (0, 10, 0)

			for ivao, vao in enumerate(self.vaos_scene):
			
				self.color.value = tuple(self.scene.meshes[ivao].material.color[:3])
				vao.render()
		else:
			self.scene.draw(
				projection_matrix=self.camera.projection.matrix,
				camera_matrix=camera_matrix,
				time=time
			)

		self.ctx.finish()

		# screenshot.create(self.wnd.fbo, "jpeg", f"{Renderer.out_dir}/output{self.iscreenshot:03d}.jpg", "RGB", 4)

		data = self.wnd.fbo.read(components=3, alignment=1)
		img = Image.frombytes('RGB', self.wnd.fbo.size, data, 'raw', 'RGB', 0, -1)

		if Renderer.store_image:
			self.scene.release()
			self.wnd.fbo.release()
			self.wnd.close()
			Renderer.img = np.array(img)
			return

		img.save(f"{Renderer.out_dir}/output{self.iscreenshot:03d}.jpg")

		self.iscreenshot += 1

		# exit()

		if self.iscreenshot >= self.nscreenshot:
			self.scene.release()
			self.wnd.fbo.release()
			self.wnd.close()