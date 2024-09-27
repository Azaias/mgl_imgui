import imgui
import moderngl as mgl
from imgui.integrations import compute_fb_scale
from imgui.integrations.base import BaseOpenGLRenderer
import ctypes
import pygame as pg

from .keys_pygame import MouseButtons, MouseButtonStates, Keys


class ModernGLRendererMixin:
    def resize(self, width: int, height: int):
        self.io.display_size = (width, height)
        self.io.display_fb_scale = compute_fb_scale((width, height), self.ctx.screen.size)

    def handle_event(self, event) -> bool:
        """Returns True if event is consumed by gui, False if not."""
        result = False

        mouse = self._mouse_buttons
        mouse_states = self._mouse_states

        if event.type == pg.MOUSEMOTION:
            if mouse_states.any:
                self.mouse_drag_event(
                    event.pos[0], event.pos[1], event.rel[0], event.rel[1]
                )
                if self.io.want_capture_mouse:
                    result = True
            else:
                self.mouse_position_event(
                    event.pos[0], event.pos[1], event.rel[0], event.rel[1]
                )

        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button in [mouse.left, mouse.right, mouse.middle]:
                self.mouse_press_event(
                    event.pos[0], event.pos[1], event.button
                )
                self._handle_mouse_button_state_change(event.button, True)
                if self.io.want_capture_mouse:
                    result = True

        elif event.type == pg.MOUSEBUTTONUP:
            if event.button in [mouse.left, mouse.right, mouse.middle]:
                self.mouse_release_event(
                    event.pos[0], event.pos[1], event.button
                )
                self._handle_mouse_button_state_change(event.button, False)

        elif event.type in [pg.KEYDOWN, pg.KEYUP]:
            self.key_event(event.key, event.type)

        elif event.type == pg.TEXTINPUT:
            self.unicode_char_entered(event.text)

        elif event.type == pg.MOUSEWHEEL:
            self.mouse_scroll_event(float(event.x), float(event.y))
            if imgui.is_any_item_hovered():
                result = True

        elif event.type == pg.VIDEORESIZE:
            self.resize(event.size[0], event.size[1])

        return result

    def key_event(self, key, action):
        keys = self._keys

        if action == keys.ACTION_PRESS:
            if key in self.REVERSE_KEY_MAP:
                self.io.keys_down[self.REVERSE_KEY_MAP[key]] = True
        else:
            if key in self.REVERSE_KEY_MAP:
                self.io.keys_down[self.REVERSE_KEY_MAP[key]] = False

    def _mouse_pos_viewport(self, x, y):
        """Make sure coordinates are correct with black borders"""
        return (
            int(
                x
                - (self._display_size[0] - self._viewport_size[0] / self._pixel_ratio) / 2
            ),
            int(
                y
                - (self._display_size[1] - self._viewport_size[1] / self._pixel_ratio)
                / 2
            ),
        )

    def _handle_mouse_button_state_change(self, button, pressed: bool):
        if button == self._mouse_buttons.left:
            self._mouse_states.left = pressed
        elif button == self._mouse_buttons.right:
            self._mouse_states.right = pressed
        elif button == self._mouse_buttons.middle:
            self._mouse_states.middle = pressed
        else:
            raise ValueError("Incompatible mouse button number: {}".format(button))

    def mouse_position_event(self, x, y, dx, dy):
        self.io.mouse_pos = self._mouse_pos_viewport(x, y)

    def mouse_drag_event(self, x, y, dx, dy):
        self.io.mouse_pos = self._mouse_pos_viewport(x, y)

        if self._mouse_states.left:
            self.io.mouse_down[0] = 1

        if self._mouse_states.middle:
            self.io.mouse_down[2] = 1

        if self._mouse_states.right:
            self.io.mouse_down[1] = 1

    def mouse_scroll_event(self, x_offset, y_offset):
        self.io.mouse_wheel = y_offset

    def mouse_press_event(self, x, y, button):
        self.io.mouse_pos = self._mouse_pos_viewport(x, y)

        if button == self._mouse_buttons.left:
            self.io.mouse_down[0] = 1

        if button == self._mouse_buttons.middle:
            self.io.mouse_down[2] = 1

        if button == self._mouse_buttons.right:
            self.io.mouse_down[1] = 1

    def mouse_release_event(self, x, y, button):
        self.io.mouse_pos = self._mouse_pos_viewport(x, y)

        if button == self._mouse_buttons.left:
            self.io.mouse_down[0] = 0

        if button == self._mouse_buttons.middle:
            self.io.mouse_down[2] = 0

        if button == self._mouse_buttons.right:
            self.io.mouse_down[1] = 0

    def unicode_char_entered(self, char):
        io = imgui.get_io()
        io.add_input_character(ord(char))


class ModernGLBaseRenderer(BaseOpenGLRenderer):

    VERTEX_SHADER_SRC = """
            #version 330
            uniform mat4 ProjMtx;
            in vec2 Position;
            in vec2 UV;
            in vec4 Color;
            out vec2 Frag_UV;
            out vec4 Frag_Color;
            void main() {
                Frag_UV = UV;
                Frag_Color = Color;
                gl_Position = ProjMtx * vec4(Position.xy, 0, 1);
            }
        """
    FRAGMENT_SHADER_SRC = """
            #version 330
            uniform sampler2D Texture;
            in vec2 Frag_UV;
            in vec4 Frag_Color;
            out vec4 Out_Color;
            void main() {
                Out_Color = (Frag_Color * texture(Texture, Frag_UV.st));
            }
        """

    def __init__(self, *args, **kwargs):
        self._prog = None
        self._fbo = None
        self._font_texture = None
        self._vertex_buffer = None
        self._index_buffer = None
        self._vao = None
        self._textures = {}
        self.ctx: mgl.Context = kwargs.get("ctx")

        if not self.ctx:
            raise ValueError("Missing moderngl context")

        assert isinstance(self.ctx, mgl.Context)

        super().__init__()

        display_size = kwargs.get('display_size')
        self.resize(*display_size)

    def register_texture(self, texture: mgl.Texture):
        if texture.glo not in self._textures:
            self._textures[texture.glo] = texture

    def remove_texture(self, texture: mgl.Texture):
        del self._textures[texture.glo]

    def refresh_font_texture(self):
        width, height, pixels = self.io.fonts.get_tex_data_as_rgba32()

        if self._font_texture:
            self.remove_texture(self._font_texture)
            self._font_texture.release()

        self._font_texture = self.ctx.texture((width, height), 4, data=pixels)
        self.register_texture(self._font_texture)
        self.io.fonts.texture_id = self._font_texture.glo
        self.io.fonts.clear_tex_data()

    def _create_device_objects(self):
        self._prog = self.ctx.program(
            vertex_shader=self.VERTEX_SHADER_SRC,
            fragment_shader=self.FRAGMENT_SHADER_SRC
        )
        self.projMat = self._prog["ProjMtx"]
        self._prog["Texture"].value = 0
        self._vertex_buffer = self.ctx.buffer(reserve=imgui.VERTEX_SIZE * 65536)
        self._index_buffer = self.ctx.buffer(reserve=imgui.INDEX_SIZE * 65536)
        self._vao = self.ctx.vertex_array(
            self._prog,
            [(self._vertex_buffer, "2f 2f 4f1", "Position", "UV", "Color")],
            index_buffer=self._index_buffer,
            index_element_size=imgui.INDEX_SIZE
        )

    def render(self, draw_data):
        io = self.io
        display_width, display_height = io.display_size
        fb_width = int(display_width * io.display_fb_scale[0])
        fb_height = int(display_height * io.display_fb_scale[1])

        if fb_width == 0 or fb_height == 0:
            return

        self.projMat.value = (
            2.0 / display_width,
            0.0,
            0.0,
            0.0,
            0.0,
            2.0 / -display_height,
            0.0,
            0.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            -1.0,
            1.0,
            0.0,
            1.0,
        )

        draw_data.scale_clip_rects(*io.display_fb_scale)

        self.ctx.enable_only(mgl.BLEND)
        self.ctx.blend_equation = mgl.FUNC_ADD
        self.ctx.blend_func = mgl.SRC_ALPHA, mgl.ONE_MINUS_SRC_ALPHA

        self._font_texture.use()

        for commands in draw_data.commands_lists:
            # Write the vertex and index buffer data without copying it
            vtx_type = ctypes.c_byte * commands.vtx_buffer_size * imgui.VERTEX_SIZE
            idx_type = ctypes.c_byte * commands.idx_buffer_size * imgui.INDEX_SIZE
            vtx_arr = (vtx_type).from_address(commands.vtx_buffer_data)
            idx_arr = (idx_type).from_address(commands.idx_buffer_data)
            self._vertex_buffer.write(vtx_arr)
            self._index_buffer.write(idx_arr)

            idx_pos = 0
            for command in commands.commands:
                texture = self._textures.get(command.texture_id)
                if texture is None:
                    raise ValueError(
                        (
                            "Texture {} is not registered. Please add to renderer using "
                            "register_texture(..). "
                            "Current textures: {}".format(
                                command.texture_id, list(self._textures)
                            )
                        )
                    )

                texture.use(0)

                x, y, z, w = command.clip_rect
                self.ctx.scissor = int(x), int(fb_height - w), int(z - x), int(w - y)
                self._vao.render(
                    mgl.TRIANGLES, vertices=command.elem_count, first=idx_pos
                )
                idx_pos += command.elem_count

        self.ctx.scissor = None

    def _invalidate_device_objects(self):
        if self._font_texture:
            self._font_texture.release()
        if self._vertex_buffer:
            self._vertex_buffer.release()
        if self._index_buffer:
            self._index_buffer.release()
        if self._vao:
            self._vao.release()
        if self._prog:
            self._prog.release()

        self.io.fonts.texture_id = 0
        self._font_texture = None


class ModernGLRenderer(ModernGLBaseRenderer, ModernGLRendererMixin):
    def __init__(self, ctx, display_size):
        super().__init__(ctx=ctx, display_size=display_size)
        self._keys = Keys
        self._mouse_buttons = MouseButtons
        self._mouse_states = MouseButtonStates()

        self._display_size = display_size
        self._pixel_ratio = self.ctx.screen.width / display_size[0]
        self._viewport_size = self.ctx.viewport[2:]

        self._init_key_maps()
        self.io.display_size = display_size
        self.io.display_fb_scale = self._pixel_ratio, self._pixel_ratio

        self._gui_time = None

    def _init_key_maps(self):
        keys = self._keys

        self.REVERSE_KEY_MAP = {
            keys.TAB: imgui.KEY_TAB,
            keys.LEFT: imgui.KEY_LEFT_ARROW,
            keys.RIGHT: imgui.KEY_RIGHT_ARROW,
            keys.UP: imgui.KEY_UP_ARROW,
            keys.DOWN: imgui.KEY_DOWN_ARROW,
            keys.PAGE_UP: imgui.KEY_PAGE_UP,
            keys.PAGE_DOWN: imgui.KEY_PAGE_DOWN,
            keys.HOME: imgui.KEY_HOME,
            keys.END: imgui.KEY_END,
            keys.DELETE: imgui.KEY_DELETE,
            keys.SPACE: imgui.KEY_SPACE,
            keys.BACKSPACE: imgui.KEY_BACKSPACE,
            keys.ENTER: imgui.KEY_ENTER,
            keys.NUMPAD_ENTER: imgui.KEY_PAD_ENTER,
            keys.ESCAPE: imgui.KEY_ESCAPE,
            keys.A: imgui.KEY_A,
            keys.C: imgui.KEY_C,
            keys.V: imgui.KEY_V,
            keys.X: imgui.KEY_X,
            keys.Y: imgui.KEY_Y,
            keys.Z: imgui.KEY_Z,
        }

        for value in self.REVERSE_KEY_MAP.values():
            self.io.key_map[value] = value

    @staticmethod
    def process_inputs(delta_time: float):
        if delta_time <= 0.0:
            delta_time = 1 / 1000
        io = imgui.get_io()
        io.delta_time = delta_time
