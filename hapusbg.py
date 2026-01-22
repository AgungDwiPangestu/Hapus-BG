import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
import os
import threading

class BackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 Hapus Background - Background Remover")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.tolerance = tk.IntVar(value=50)
        self.target_color = (0, 255, 0)  # Default green screen
        self.original_image = None
        self.preview_image = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎨 Hapus Background", font=("Segoe UI", 20, "bold"))
        title_label.pack(pady=(0, 10))
        
        subtitle = ttk.Label(main_frame, text="Hapus warna tertentu dan jadikan transparan", font=("Segoe UI", 10))
        subtitle.pack(pady=(0, 15))
        
        # === INPUT FILE SECTION ===
        input_frame = ttk.LabelFrame(main_frame, text="📁 File Input", padding="10")
        input_frame.pack(fill=tk.X, pady=5)
        
        input_entry = ttk.Entry(input_frame, textvariable=self.input_path, width=60)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(input_frame, text="Pilih File...", command=self.browse_input)
        browse_btn.pack(side=tk.RIGHT)
        
        # === OUTPUT FILE SECTION ===
        output_frame = ttk.LabelFrame(main_frame, text="💾 File Output", padding="10")
        output_frame.pack(fill=tk.X, pady=5)
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path, width=60)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        save_btn = ttk.Button(output_frame, text="Simpan Ke...", command=self.browse_output)
        save_btn.pack(side=tk.RIGHT)
        
        # === COLOR SETTINGS SECTION ===
        color_frame = ttk.LabelFrame(main_frame, text="🎨 Pengaturan Warna", padding="10")
        color_frame.pack(fill=tk.X, pady=5)
        
        # Preset colors row
        preset_frame = ttk.Frame(color_frame)
        preset_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(preset_frame, text="Warna Preset:").pack(side=tk.LEFT, padx=(0, 10))
        
        # Green Screen button
        self.green_btn = tk.Button(preset_frame, text="Green Screen", bg="#00FF00", fg="black",
                                   command=lambda: self.set_color((0, 255, 0)), width=12)
        self.green_btn.pack(side=tk.LEFT, padx=5)
        
        # White button
        self.white_btn = tk.Button(preset_frame, text="Putih", bg="#FFFFFF", fg="black",
                                   command=lambda: self.set_color((255, 255, 255)), width=12)
        self.white_btn.pack(side=tk.LEFT, padx=5)
        
        # Black button
        self.black_btn = tk.Button(preset_frame, text="Hitam", bg="#000000", fg="white",
                                   command=lambda: self.set_color((0, 0, 0)), width=12)
        self.black_btn.pack(side=tk.LEFT, padx=5)
        
        # Blue Screen button
        self.blue_btn = tk.Button(preset_frame, text="Blue Screen", bg="#0000FF", fg="white",
                                  command=lambda: self.set_color((0, 0, 255)), width=12)
        self.blue_btn.pack(side=tk.LEFT, padx=5)
        
        # Custom color row
        custom_frame = ttk.Frame(color_frame)
        custom_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(custom_frame, text="Warna Custom:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.color_preview = tk.Label(custom_frame, text="", bg="#00FF00", width=8, height=1, relief="solid")
        self.color_preview.pack(side=tk.LEFT, padx=5)
        
        self.color_label = ttk.Label(custom_frame, text="RGB: (0, 255, 0)")
        self.color_label.pack(side=tk.LEFT, padx=10)
        
        pick_color_btn = ttk.Button(custom_frame, text="Pilih Warna...", command=self.pick_color)
        pick_color_btn.pack(side=tk.LEFT, padx=5)
        
        pick_from_image_btn = ttk.Button(custom_frame, text="Ambil dari Gambar", command=self.enable_color_picker)
        pick_from_image_btn.pack(side=tk.LEFT, padx=5)
        
        # Tolerance slider
        tolerance_frame = ttk.Frame(color_frame)
        tolerance_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(tolerance_frame, text="Toleransi:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.tolerance_slider = ttk.Scale(tolerance_frame, from_=0, to=255, 
                                          variable=self.tolerance, orient=tk.HORIZONTAL, length=300)
        self.tolerance_slider.pack(side=tk.LEFT, padx=5)
        
        self.tolerance_label = ttk.Label(tolerance_frame, text="50")
        self.tolerance_label.pack(side=tk.LEFT, padx=10)
        
        self.tolerance.trace_add("write", self.update_tolerance_label)
        
        # === PREVIEW SECTION ===
        preview_frame = ttk.LabelFrame(main_frame, text="👁️ Preview Gambar", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Canvas for image preview
        self.canvas = tk.Canvas(preview_frame, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        self.picking_color = False
        
        # === PROGRESS BAR ===
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(main_frame, text="Siap memproses gambar", font=("Segoe UI", 9))
        self.status_label.pack(pady=5)
        
        # === ACTION BUTTONS ===
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        preview_btn = ttk.Button(button_frame, text="🔍 Preview Hasil", command=self.preview_result)
        preview_btn.pack(side=tk.LEFT, padx=5)
        
        process_btn = ttk.Button(button_frame, text="✨ Proses & Simpan", command=self.process_image)
        process_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = ttk.Button(button_frame, text="🔄 Reset", command=self.reset_app)
        reset_btn.pack(side=tk.RIGHT, padx=5)
    
    def browse_input(self):
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Pilih Gambar", filetypes=filetypes)
        if filename:
            self.input_path.set(filename)
            # Auto-set output path
            base, ext = os.path.splitext(filename)
            self.output_path.set(f"{base}_transparent.png")
            self.load_preview()
    
    def browse_output(self):
        filetypes = [("PNG files", "*.png")]
        filename = filedialog.asksaveasfilename(title="Simpan Sebagai", 
                                                 defaultextension=".png",
                                                 filetypes=filetypes)
        if filename:
            self.output_path.set(filename)
    
    def set_color(self, color):
        self.target_color = color
        hex_color = "#{:02x}{:02x}{:02x}".format(*color)
        self.color_preview.config(bg=hex_color)
        self.color_label.config(text=f"RGB: {color}")
    
    def pick_color(self):
        color = colorchooser.askcolor(title="Pilih Warna yang Akan Dihapus")
        if color[0]:
            rgb = tuple(int(c) for c in color[0])
            self.set_color(rgb)
    
    def enable_color_picker(self):
        if not self.original_image:
            messagebox.showwarning("Peringatan", "Silakan pilih gambar terlebih dahulu!")
            return
        self.picking_color = True
        self.status_label.config(text="🎯 Klik pada gambar untuk memilih warna...")
        self.canvas.config(cursor="crosshair")
    
    def on_canvas_click(self, event):
        if not self.picking_color or not self.original_image:
            return
        
        # Get canvas dimensions and image dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        img_width, img_height = self.original_image.size
        
        # Calculate scale
        scale = min(canvas_width / img_width, canvas_height / img_height)
        display_width = int(img_width * scale)
        display_height = int(img_height * scale)
        
        # Calculate offset
        x_offset = (canvas_width - display_width) // 2
        y_offset = (canvas_height - display_height) // 2
        
        # Convert canvas coordinates to image coordinates
        img_x = int((event.x - x_offset) / scale)
        img_y = int((event.y - y_offset) / scale)
        
        # Check bounds
        if 0 <= img_x < img_width and 0 <= img_y < img_height:
            pixel = self.original_image.convert("RGB").getpixel((img_x, img_y))
            self.set_color(pixel)
            self.status_label.config(text=f"Warna dipilih: RGB{pixel}")
        
        self.picking_color = False
        self.canvas.config(cursor="")
    
    def update_tolerance_label(self, *args):
        self.tolerance_label.config(text=str(self.tolerance.get()))
    
    def load_preview(self):
        try:
            self.original_image = Image.open(self.input_path.get())
            self.display_image(self.original_image)
            self.status_label.config(text=f"Gambar dimuat: {self.original_image.size[0]}x{self.original_image.size[1]} pixel")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat gambar: {e}")
    
    def display_image(self, img):
        # Get canvas size
        self.canvas.update()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 600, 300
        
        # Scale image to fit canvas
        img_ratio = img.size[0] / img.size[1]
        canvas_ratio = canvas_width / canvas_height
        
        if img_ratio > canvas_ratio:
            new_width = canvas_width - 20
            new_height = int(new_width / img_ratio)
        else:
            new_height = canvas_height - 20
            new_width = int(new_height * img_ratio)
        
        # Resize for display
        display_img = img.copy()
        display_img.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.preview_image = ImageTk.PhotoImage(display_img)
        
        # Clear canvas and display image
        self.canvas.delete("all")
        x = canvas_width // 2
        y = canvas_height // 2
        self.canvas.create_image(x, y, anchor=tk.CENTER, image=self.preview_image)
    
    def make_transparent(self, input_path, output_path=None, preview_only=False):
        try:
            img = Image.open(input_path)
            img = img.convert("RGBA")
            
            pixels = list(img.getdata())
            total_pixels = len(pixels)
            
            tr, tg, tb = self.target_color
            tol = self.tolerance.get()
            
            new_data = []
            
            for i, item in enumerate(pixels):
                # Update progress
                if i % 10000 == 0:
                    progress = (i / total_pixels) * 100
                    self.progress_var.set(progress)
                    self.root.update_idletasks()
                
                # Check if pixel matches target color within tolerance
                if (abs(item[0] - tr) <= tol and 
                    abs(item[1] - tg) <= tol and 
                    abs(item[2] - tb) <= tol):
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            
            img.putdata(new_data)
            self.progress_var.set(100)
            
            if preview_only:
                return img
            else:
                img.save(output_path, "PNG")
                return True
                
        except Exception as e:
            raise e
    
    def preview_result(self):
        if not self.input_path.get():
            messagebox.showwarning("Peringatan", "Silakan pilih file input terlebih dahulu!")
            return
        
        self.status_label.config(text="Sedang membuat preview...")
        self.progress_var.set(0)
        
        def process():
            try:
                result_img = self.make_transparent(self.input_path.get(), preview_only=True)
                
                # Create checkerboard background for transparency visualization
                checker = self.create_checkerboard(result_img.size)
                checker.paste(result_img, (0, 0), result_img)
                
                self.root.after(0, lambda: self.display_image(checker))
                self.root.after(0, lambda: self.status_label.config(text="Preview selesai! (Background kotak-kotak = transparan)"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Gagal membuat preview: {e}"))
                self.root.after(0, lambda: self.status_label.config(text="Gagal membuat preview"))
        
        threading.Thread(target=process, daemon=True).start()
    
    def create_checkerboard(self, size, square_size=10):
        """Create a checkerboard pattern to visualize transparency"""
        checker = Image.new("RGBA", size, (255, 255, 255, 255))
        for y in range(0, size[1], square_size):
            for x in range(0, size[0], square_size):
                if (x // square_size + y // square_size) % 2 == 0:
                    for py in range(y, min(y + square_size, size[1])):
                        for px in range(x, min(x + square_size, size[0])):
                            checker.putpixel((px, py), (200, 200, 200, 255))
        return checker
    
    def process_image(self):
        if not self.input_path.get():
            messagebox.showwarning("Peringatan", "Silakan pilih file input terlebih dahulu!")
            return
        
        if not self.output_path.get():
            messagebox.showwarning("Peringatan", "Silakan tentukan lokasi file output!")
            return
        
        self.status_label.config(text="Sedang memproses gambar...")
        self.progress_var.set(0)
        
        def process():
            try:
                self.make_transparent(self.input_path.get(), self.output_path.get())
                self.root.after(0, lambda: messagebox.showinfo("Sukses", 
                    f"✨ Gambar berhasil diproses!\n\nDisimpan di:\n{self.output_path.get()}"))
                self.root.after(0, lambda: self.status_label.config(text="Selesai! Gambar telah disimpan."))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Gagal memproses gambar: {e}"))
                self.root.after(0, lambda: self.status_label.config(text="Gagal memproses gambar"))
        
        threading.Thread(target=process, daemon=True).start()
    
    def reset_app(self):
        self.input_path.set("")
        self.output_path.set("")
        self.tolerance.set(50)
        self.set_color((0, 255, 0))
        self.original_image = None
        self.preview_image = None
        self.canvas.delete("all")
        self.progress_var.set(0)
        self.status_label.config(text="Siap memproses gambar")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    
    # Set theme style
    style = ttk.Style()
    style.theme_use('clam')
    
    app = BackgroundRemoverApp(root)
    root.mainloop()