"""
FITS Image Preview Window Module

Provides a popup window for previewing FITS images with auto-stretch.
"""

import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
import logging
import threading
import numpy as np
from astropy.io import fits
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)


class PreviewWindow(ctk.CTkToplevel):
    """Window for previewing FITS images."""
    
    def __init__(self, parent, image_path: Path):
        super().__init__(parent)
        self.parent = parent
        self.image_path = image_path
        
        self.title(f"Image Preview - {image_path.name}")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.setup_ui()
        
        # Load image in background thread
        self.loading_label = ctk.CTkLabel(self.main_frame, text="Loading image...", font=ctk.CTkFont(size=14))
        self.loading_label.pack(pady=50)
        
        thread = threading.Thread(target=self.load_image)
        thread.daemon = True
        thread.start()
    
    def setup_ui(self):
        """Setup the preview window UI."""
        # Main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Preview: {self.image_path.name}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(0, 10))
        
        # Image container
        self.image_frame = ctk.CTkFrame(self.main_frame, fg_color="black")
        self.image_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Image label
        self.image_label = ctk.CTkLabel(self.image_frame, text="")
        self.image_label.pack(expand=True)
        
        # Info frame
        self.info_frame = ctk.CTkFrame(self.main_frame)
        self.info_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Dimensions: - | Bit depth: -",
            font=ctk.CTkFont(size=12)
        )
        self.info_label.pack(pady=5)
        
        # Close button
        self.close_button = ctk.CTkButton(
            self.main_frame,
            text="Close",
            command=self.destroy,
            height=35
        )
        self.close_button.pack(pady=(0, 10))
    
    def load_image(self):
        """Load and display the FITS image with auto-stretch."""
        try:
            # Load FITS data
            with fits.open(self.image_path) as hdul:
                # Get primary data
                data = hdul[0].data
                header = hdul[0].header
                
                # Handle 3D data (RGB) vs 2D (grayscale)
                if data is None:
                    self.after(0, lambda: self.show_error("No image data found"))
                    return
                
                # Get dimensions
                if len(data.shape) == 3:
                    # RGB image - take first channel or convert
                    if data.shape[0] == 3:
                        # CHW format
                        data = np.transpose(data, (1, 2, 0))
                    height, width = data.shape[:2]
                    is_color = True
                else:
                    # Grayscale
                    height, width = data.shape
                    is_color = False
                
                # Apply auto-stretch (percentile stretch)
                stretched = self.auto_stretch(data)
                
                # Convert to PIL Image
                if is_color:
                    image = Image.fromarray((stretched * 255).astype(np.uint8), mode='RGB')
                else:
                    image = Image.fromarray((stretched * 255).astype(np.uint8), mode='L')
                
                # Resize to fit window while maintaining aspect ratio
                max_size = (750, 450)
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to CTkImage
                ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
                
                # Get bit depth from header
                bitpix = header.get('BITPIX', 'Unknown')
                
                # Update UI on main thread
                self.after(0, lambda: self.display_image(ctk_image, width, height, bitpix))
                
        except Exception as e:
            logger.error(f"Failed to load preview: {e}")
            self.after(0, lambda: self.show_error(str(e)))
    
    def auto_stretch(self, data: np.ndarray) -> np.ndarray:
        """Apply auto-stretch to FITS data for visibility."""
        # Handle different data types
        if data.dtype == np.uint16:
            # 16-bit data
            data = data.astype(np.float32) / 65535.0
        elif data.dtype == np.uint8:
            # 8-bit data
            data = data.astype(np.float32) / 255.0
        else:
            # Already float or other - normalize
            data = data.astype(np.float32)
        
        # For RGB, process each channel
        if len(data.shape) == 3 and data.shape[2] == 3:
            result = np.zeros_like(data)
            for i in range(3):
                result[:, :, i] = self._stretch_channel(data[:, :, i])
            return result
        else:
            return self._stretch_channel(data)
    
    def _stretch_channel(self, channel: np.ndarray) -> np.ndarray:
        """Apply percentile stretch to a single channel."""
        # Clip extreme values
        low, high = np.percentile(channel[channel > 0], [1, 99]) if np.any(channel > 0) else (0, 1)
        
        if high > low:
            stretched = (channel - low) / (high - low)
        else:
            stretched = channel
        
        # Clip to 0-1 range
        return np.clip(stretched, 0, 1)
    
    def display_image(self, image, width: int, height: int, bitpix):
        """Display the loaded image."""
        self.loading_label.destroy()
        self.image_label.configure(image=image)
        self.image_label.image = image  # Keep reference
        
        # Update info
        bit_depth = {
            8: '8-bit',
            16: '16-bit',
            32: '32-bit',
            -32: '32-bit float',
            -64: '64-bit float'
        }.get(bitpix, f'BITPIX={bitpix}')
        
        self.info_label.configure(text=f"Dimensions: {width} x {height} pixels | Bit depth: {bit_depth}")
    
    def show_error(self, message: str):
        """Show error message."""
        self.loading_label.destroy()
        error_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Error loading image:\n{message}",
            font=ctk.CTkFont(size=12),
            text_color="red"
        )
        error_label.pack(pady=50)
        messagebox.showerror("Preview Error", f"Failed to load image preview: {message}")
