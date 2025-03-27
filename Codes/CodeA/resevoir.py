import serial
import time
from PIL import Image
import os
from datetime import datetime

class OV7670_Receiver:
    def __init__(self, port='COM3', baudrate=921600, width=320, height=240):
        self.port = port
        self.baudrate = baudrate
        self.width = width
        self.height = height
        self.ser = None
        self.image_dir = "captures"
        self.create_image_dir()
        
        # Protocole
        self.SYNC_HEADER = 0xAA
        self.SYNC_FOOTER = 0x55
        self.CAPTURE_CMD = b'C'
        self.TIMEOUT = 3.0  # seconds
        
    def create_image_dir(self):
        """Crée le dossier de sauvegarde des images"""
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
            
    def connect(self):
        """Établit la connexion série"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                write_timeout=1
            )
            time.sleep(2)  # Important pour l'initialisation
            print(f"Connecté à {self.ser.port} à {self.baudrate} bauds")
            return True
        except Exception as e:
            print(f"Erreur de connexion: {str(e)}")
            return False
            
    def disconnect(self):
        """Ferme la connexion série"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Connexion fermée")
            
    def send_command(self, cmd):
        """Envoie une commande à l'Arduino"""
        try:
            self.ser.reset_input_buffer()
            self.ser.write(cmd)
            self.ser.flush()
            return True
        except Exception as e:
            print(f"Erreur d'envoi: {str(e)}")
            return False
            
    def wait_for_sync(self, sync_byte, timeout=None):
        """Attend un byte de synchronisation"""
        timeout = timeout or self.TIMEOUT
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.ser.in_waiting > 0:
                byte = ord(self.ser.read(1))
                if byte == sync_byte:
                    return True
        return False
        
    def read_image_data(self, expected_size):
        """Lit les données d'image avec timeout"""
        data = bytearray()
        start_time = time.time()
        
        while len(data) < expected_size and (time.time() - start_time) < self.TIMEOUT:
            remaining = expected_size - len(data)
            chunk = self.ser.read(remaining)
            data.extend(chunk)
            
        return data if len(data) == expected_size else None
        
    def yuv_to_rgb(self, y, u, v):
        """Convertit YUV en RGB"""
        r = max(0, min(255, y + 1.402 * (v - 128)))
        g = max(0, min(255, y - 0.34414 * (u - 128) - 0.71414 * (v - 128)))
        b = max(0, min(255, y + 1.772 * (u - 128)))
        return (int(r), int(g), int(b))
        
    def process_frames(self, y_data, uv_data):
        """Traite les frames Y et UV pour créer une image RGB"""
        rgb_image = []
        for i in range(self.width * self.height):
            y = y_data[i]
            # Format YUV422: échantillonnage UV réduit
            uv_index = (i // 2) * 2
            u = uv_data[uv_index]
            v = uv_data[uv_index + 1] if (uv_index + 1) < len(uv_data) else uv_data[uv_index]
            rgb_image.append(self.yuv_to_rgb(y, u, v))
        return rgb_image
        
    def save_images(self, y_data, uv_data, rgb_data, prefix=""):
        """Sauvegarde les différentes versions de l'image"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Image RGB
        img_rgb = Image.new('RGB', (self.width, self.height))
        img_rgb.putdata(rgb_data)
        img_rgb.save(f"{self.image_dir}/{prefix}rgb_{timestamp}.png")
        
        # Composante Y (Luminance)
        img_y = Image.new('L', (self.width, self.height))
        img_y.putdata(y_data)
        img_y.save(f"{self.image_dir}/{prefix}y_{timestamp}.png")
        
        # Composante UV (Chrominance)
        img_uv = Image.new('L', (self.width, self.height))
        img_uv.putdata(uv_data)
        img_uv.save(f"{self.image_dir}/{prefix}uv_{timestamp}.png")
        
    def capture(self):
        """Capture une image complète"""
        if not self.send_command(self.CAPTURE_CMD):
            return False
            
        # Attente de l'en-tête
        if not self.wait_for_sync(self.SYNC_HEADER):
            print("Timeout: En-tête non reçu")
            return False
            
        # Lecture des données Y
        y_data = self.read_image_data(self.width * self.height)
        if not y_data:
            print("Erreur: Données Y incomplètes")
            return False
            
        # Lecture des données UV
        uv_data = self.read_image_data(self.width * self.height)
        if not uv_data:
            print("Erreur: Données UV incomplètes")
            return False
            
        # Vérification du pied de page
        if not self.wait_for_sync(self.SYNC_FOOTER, timeout=1.0):
            print("Avertissement: Pied de page manquant")
            
        # Traitement des images
        rgb_data = self.process_frames(y_data, uv_data)
        self.save_images(y_data, uv_data, rgb_data)
        
        return True
        
    def run(self, max_attempts=10):
        """Exécute la capture en boucle"""
        if not self.connect():
            return
            
        attempt = 0
        while attempt < max_attempts:
            print(f"\nTentative de capture #{attempt + 1}")
            
            if self.capture():
                print("Capture réussie!")
                break
            else:
                print("Échec de la capture, nouvelle tentative...")
                time.sleep(1)
                attempt += 1
                
        self.disconnect()

if __name__ == "__main__":
    receiver = OV7670_Receiver(port='COM3', baudrate=921600)
    receiver.run(max_attempts=20)