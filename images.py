import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageTk, ImageDraw
import random

class PixelArtEditor:
    def __init__(self, root, width=25, height=25, cell_size=20):
        self.root = root
        self.cell_size = cell_size

        self.width = width
        self.height = height
        self.grid = [["#FFFFFF" for _ in range(width)] for _ in range(height)]  # Initialize grid with white color
        self.canvas = tk.Canvas(root, width=width * self.cell_size, height=height * self.cell_size)
        self.canvas.pack(side=tk.RIGHT)
        
        self.primary_color = "#000000"  # Black in hex
        self.secondary_color = "#FFFFFF"  # White in hex
        self.current_color = self.primary_color
        self.tool = "pen"  # Default tool

        self.create_grid()
        self.canvas.bind("<Button-1>", self.paint_or_fill)
        self.canvas.bind("<B1-Motion>", self.paint_or_fill)
        self.root.bind("<space>", self.switch_color)

        # Create and load placeholder icons
        self.icons = {
            'save': self.create_icon('blue'),
            'primary_color': self.create_icon(self.primary_color),
            'secondary_color': self.create_icon(self.secondary_color),
            'pen': self.create_icon('black'),
            'bucket': self.create_icon('yellow'),
            'dither': self.create_icon('red')
        }
        
        # Add buttons with icons and labels
        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.add_button_with_label(self.buttons_frame, self.icons['save'], self.save_image, "Save")
        self.primary_color_button = self.add_button_with_label(self.buttons_frame, self.icons['primary_color'], self.choose_primary_color, "Primary Color")
        self.secondary_color_button = self.add_button_with_label(self.buttons_frame, self.icons['secondary_color'], self.choose_secondary_color, "Secondary Color")
        self.add_button_with_label(self.buttons_frame, self.icons['pen'], self.use_pen, "Pen")
        self.add_button_with_label(self.buttons_frame, self.icons['bucket'], self.use_bucket, "Bucket")
        self.add_button_with_label(self.buttons_frame, self.icons['dither'], self.use_dither, "Dither")

    def create_grid(self):
        for row in range(self.height):
            for col in range(self.width):
                self.draw_cell(row, col, "#FFFFFF")

    def draw_cell(self, row, col, color):
        x1, y1 = col * self.cell_size, row * self.cell_size
        x2, y2 = x1 + self.cell_size, y1 + self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="gray", fill=color)
        self.grid[row][col] = color

    def paint_or_fill(self, event):
        col, row = event.x // self.cell_size, event.y // self.cell_size
        if 0 <= col < self.width and 0 <= row < self.height:
            if self.tool == "pen":
                self.draw_cell(row, col, self.current_color)
            elif self.tool == "bucket":
                self.bucket_fill(col, row, self.grid[row][col], self.current_color)
            elif self.tool == "dither":
                if random.choice([True, False]):
                    self.draw_cell(row, col, self.current_color)
                else:
                    self.draw_cell(row, col, "#FFFFFF")

    def bucket_fill(self, x, y, target_color, replacement_color):
        if target_color == replacement_color or self.grid[y][x] != target_color:
            return
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if self.grid[cy][cx] == target_color:
                self.draw_cell(cy, cx, replacement_color)
                for nx, ny in ((cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)):
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        stack.append((nx, ny))

    def choose_primary_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.primary_color = color
            self.current_color = self.primary_color
            self.update_color_icon(self.primary_color_button, self.primary_color)

    def choose_secondary_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.secondary_color = color
            self.update_color_icon(self.secondary_color_button, self.secondary_color)

    def update_color_icon(self, button, color):
        icon = self.create_icon(color)
        button.config(image=icon)
        button.image = icon  # Keep a reference to prevent garbage collection

    def switch_color(self, event=None):
        self.current_color = self.secondary_color if self.current_color == self.primary_color else self.primary_color

    def use_pen(self):
        self.tool = "pen"
    
    def use_bucket(self):
        self.tool = "bucket"
    
    def use_dither(self):
        self.tool = "dither"

    def save_image(self):
        image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 0))  # Create a new image with transparency
        pixels = image.load()
        
        for row in range(self.height):
            for col in range(self.width):
                color = self.grid[row][col]
                if color != "#FFFFFF":  # If the color is not white, set the pixel color
                    pixels[col, row] = tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (255,)
                else:  # If the color is white, set the pixel to transparent
                    pixels[col, row] = (255, 255, 255, 0)
        
        image = image.resize((self.width * 10, self.height * 10), Image.NEAREST)
        image.save('icon.png')

        # Save Python-compatible list of lists with hexadecimal color codes
        with open('pixel_art_map.py', 'w') as f:
            f.write('pixel_art_map = [\n')
            for row in self.grid:
                f.write('    [' + ', '.join(f'"{color}"' for color in row) + '],\n')
            f.write(']\n')

    def create_icon(self, color):
        size = (10, 10)
        image = Image.new('RGB', size, 'white')
        draw = ImageDraw.Draw(image)
        draw.rectangle([8, 8, 24, 24], fill=color)
        return ImageTk.PhotoImage(image)

    def add_button_with_label(self, parent, icon, command, text):
        frame = tk.Frame(parent)
        button = tk.Button(frame, image=icon, command=command)
        button.pack()
        label = tk.Label(frame, text=text)
        label.pack()
        frame.pack(pady=5)
        return button

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pixel Art Editor")
    editor = PixelArtEditor(root)
    root.mainloop()
