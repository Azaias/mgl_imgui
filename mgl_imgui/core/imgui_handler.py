import imgui
from ._mgl_imgui import ModernGLRenderer
import time


class ModernGLImgui:
    def __init__(self, ctx, display_size):
        imgui.create_context()
        self.renderer = ModernGLRenderer(ctx=ctx, display_size=display_size)
        self._start_time = time.time()

    def handle_event(self, event):
        """ Takes a pygame event as a parameter. Returns True if event should be discarded """
        event_consumed = self.renderer.handle_event(event=event)
        return event_consumed

    def render(self):
        runtime = time.time() - self._start_time
        self.renderer.process_inputs(runtime)
        imgui.render()
        self.renderer.render(imgui.get_draw_data())

    def full_render(self, ui_update_func):
        imgui.new_frame()
        ui_update_func()
        imgui.end_frame()
        self.render()
