import imgui
from ._mgl_imgui import ModernGLRenderer
import moderngl as mgl


class ModernGLImgui:
    def __init__(self, ctx, display_size):
        imgui.create_context()
        self._renderer = ModernGLRenderer(ctx=ctx, display_size=display_size)

    def update(self, delta_time: float):
        self._renderer.process_inputs(delta_time)

    def handle_event(self, event):
        """ Takes a pygame event as a parameter. Returns True if event should be discarded """
        event_consumed = self._renderer.handle_event(event=event)
        return event_consumed

    def render(self):
        imgui.render()
        self._renderer.render(imgui.get_draw_data())

    def register_texture(self, texture: mgl.Texture):
        self._renderer.register_texture(texture)

    def remove_texture(self, texture: mgl.Texture):
        self._renderer.remove_texture(texture)

    def shutdown(self):
        self._renderer.shutdown()
