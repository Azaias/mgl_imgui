import pygame as pg
import moderngl as mgl
import sys
from mgl_imgui import ModernGLImgui
import imgui
import time


class HighResClock:
    """ A wrapper for pygame.Clock that tracks delta_time with higher precision (in seconds). """

    def __init__(self):
        self._clock = pg.time.Clock()
        self._current_time = 0.0
        self.delta_time = 0.0

    def start(self):
        """ Start or initialize the clock """
        self.delta_time = 0.0
        self._current_time = time.perf_counter()

    def tick(self, fps_cap: int = 0) -> float:
        self._clock.tick(fps_cap)
        curr_time = time.perf_counter()
        self.delta_time = curr_time - self._current_time
        self._current_time = curr_time
        return self.delta_time

    def get_fps(self) -> int:
        return int(self._clock.get_fps())


class App:
    window_size = (1024, 768)

    def __init__(self):
        self.ctx: mgl.Context | None = None
        self.color = (0.0, 0.0, 0.0, 0.0)

        # Using custom HighResClock class because delta_time needs high precision.
        # If not, interaction with imgui widgets won't be correct at high fps values
        self.clock = HighResClock()
        self.delta_time = 0.0
        self.time = 0.0

        self._is_running = False

    def initialize(self):
        self.imgui = ModernGLImgui(self.ctx, self.window_size)

    def update(self):
        self.imgui.update(self.delta_time)

    def render(self):
        self.ctx.clear(color=self.color)
        self.render_ui()

    def render_ui(self):
        imgui.new_frame()
        #
        with imgui.begin("Example", False):
            r, g, b, a = self.color
            changed, values = imgui.drag_float4("color", r, g, b, a, 0.05, 0.0, 1.0)
            if changed:
                r, g, b, a = values
                self.color = (r, g, b, a)
        #
        imgui.end_frame()
        self.imgui.render()

    def user_input(self, event):
        """ User input handled here """
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self._is_running = False

    def handle_event(self, event):
        """ Should return True if event is consumed """
        return self.imgui.handle_event(event=event)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._is_running = False

            if self.handle_event(event=event):
                continue

            self.user_input(event=event)

    def run(self):
        self._setup()
        self.initialize()
        while self._is_running:
            self.handle_events()
            self.render()
            pg.display.flip()
            self.delta_time = self.clock.tick(120)
            self.time = pg.time.get_ticks() * 0.001
            pg.display.set_caption(f'{self.clock.get_fps()}')
        self.imgui.shutdown()
        pg.quit()
        sys.exit()

    def _setup(self):
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        pg.display.gl_set_attribute(pg.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, 1)
        pg.display.gl_set_attribute(pg.GL_DOUBLEBUFFER, 1)

        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, 24)
        pg.display.gl_set_attribute(pg.GL_STENCIL_SIZE, 8)

        pg.display.gl_set_attribute(pg.GL_MULTISAMPLEBUFFERS, 1)
        pg.display.gl_set_attribute(pg.GL_MULTISAMPLESAMPLES, 4)

        pg.display.set_mode(self.window_size, flags=pg.OPENGL | pg.DOUBLEBUF)
        self.ctx = mgl.create_context()

        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.BLEND)
        self.ctx.blend_func = (mgl.SRC_ALPHA, mgl.ONE_MINUS_SRC_ALPHA)
        self.ctx.gc_mode = 'auto'

        self.delta_time = 0.0
        self.time = 0.0
        self.clock.start()

        self._is_running = True


if __name__ == '__main__':
    app = App()
    app.run()
