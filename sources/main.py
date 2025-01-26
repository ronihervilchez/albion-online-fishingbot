from windowcapture import WindowCapture
from vision import Vision
from fishing_bot import FishermanBot
import threading
import mss
import cv2
import numpy as np
import win32gui


def debug():
    def get_window_position(window_title):
        hwnd = win32gui.FindWindow(None, window_title)
        if not hwnd:
            raise Exception(
                f"No se encontró la ventana con el título: {window_title}"
            )
        rect = win32gui.GetWindowRect(
            hwnd
        )  # Coordenadas absolutas de la ventana
        return rect  # Devuelve (left, top, right, bottom)

    try:
        # Obtener las coordenadas absolutas de la ventana del juego
        left, top, right, bottom = get_window_position("Albion Online Client")
        print(
            f"Coordenadas absolutas de la ventana: ({left}, {top}, {right}, {bottom})"
        )
        # Coordenadas relativas a la ventana del juego
        relative_region = (700, 470, 210, 55)
        # Convertir las coordenadas relativas en coordenadas absolutas
        absolute_region = {
            "left": left + relative_region[0],
            "top": top + relative_region[1],
            "width": relative_region[2],
            "height": relative_region[3],
        }
        print(f"Región absoluta ajustada: {absolute_region}")
        with mss.mss() as sct:
            while True:
                # Capturar la pantalla de la región especificada
                screenshot = np.array(sct.grab(absolute_region))
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                # Mostrar la captura en una ventana
                cv2.imshow("Captura de Región", screenshot)
                # Salir del bucle si se presiona la tecla "]"
                if cv2.waitKey(1) == ord("]"):
                    cv2.destroyAllWindows()
                    break
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # debug()
    bot = FishermanBot("bobber_2.png", "empty_bar_2.png", (700, 470, 210, 55))
    bot.init_gui()
