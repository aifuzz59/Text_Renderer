import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import torch
import folder_paths

class TextRendererNode:
    @classmethod
    def INPUT_TYPES(s):
        font_dir = os.path.join(folder_paths.base_path, "fonts")
        font_files = [f for f in os.listdir(font_dir) if f.endswith(('.ttf', '.otf'))]
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
                "font": (font_files,),
                "font_size": ("INT", {"default": 24, "min": 1}),
                "width": ("INT", {"default": 512, "min": 64, "max": 4096}),
                "height": ("INT", {"default": 512, "min": 64, "max": 4096}),
                "background_color": ("COLOR", {"default": "#000000"}),
                "text_color": ("COLOR", {"default": "#FFFFFF"}),
                "horizontal_align": (["left", "center", "right"],),
                "vertical_align": (["top", "middle", "bottom"],),
                "x_offset": ("INT", {"default": 0, "min": -4096, "max": 4096}),
                "y_offset": ("INT", {"default": 0, "min": -4096, "max": 4096}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "render_text"
    CATEGORY = "image/generation"

    def render_text(self, text, font, font_size, width, height, background_color, text_color, horizontal_align, vertical_align, x_offset, y_offset):
        # Create image
        image = Image.new('RGB', (width, height), color=background_color)
        draw = ImageDraw.Draw(image)

        # Load font
        font_path = os.path.join(folder_paths.base_path, "fonts", font)
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"Font file not found: {font_path}. Using default font.")
            font = ImageFont.load_default()

        # Calculate text size
        left, top, right, bottom = font.getbbox(text)
        text_width = right - left
        text_height = bottom - top

        # Calculate position based on alignment and offset
        if horizontal_align == "left":
            x = 0
        elif horizontal_align == "center":
            x = (width - text_width) // 2
        else:  # right
            x = width - text_width

        if vertical_align == "top":
            y = 0
        elif vertical_align == "middle":
            y = (height - text_height) // 2
        else:  # bottom
            y = height - text_height

        # Apply offsets
        x += x_offset
        y += y_offset

        # Draw text
        draw.text((x, y), text, font=font, fill=text_color)

        # Convert to numpy array, then to torch tensor
        img_np = np.array(image).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_np).permute(2, 0, 1)

        return (img_tensor,)

NODE_CLASS_MAPPINGS = {
    "TextRendererNode": TextRendererNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextRendererNode": "Text Renderer"
}