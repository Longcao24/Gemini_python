import speech_recognition as sr
from gtts import gTTS
import os
import datetime
import webbrowser
import pygame
import google.generativeai as genai
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class TroLyAo:
    def __init__(self, api_key):
        self.recognizer = sr.Recognizer()
        pygame.mixer.init()

        # Initialize pygame for facial expressions
        pygame.init()
        self.screen_width, self.screen_height = 400, 400
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Robot Assistant")

        # Load facial expression images
        self.expressions = {
            'normal': self.load_image('normal_face.png'),
            'speaking': self.load_image('talking_face.png'),
            'listening': self.load_image('normal_face.png')
        }

        # Set initial expression
        self.current_expression = 'normal'

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

        # Initialize Spotify client
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id="c2e4832453634e619620b86695482bb2",
            client_secret="a4ed235ec2814129b27d6cb7704404e4",
            redirect_uri="http://localhost:8888/callback",
            scope="user-modify-playback-state user-read-playback-state"
        ))

    def load_image(self, filename):
        """
        Load an image with error handling
        """
        try:
            # Assume images are in a 'faces' subdirectory
            image_path = os.path.join('faces', filename)
            image = pygame.image.load(image_path)
            return pygame.transform.scale(image, (self.screen_width, self.screen_height))
        except Exception as e:
            print(f"Error loading image {filename}: {e}")
            # Create a simple default face if image loading fails
            return self.create_default_face()

    def create_default_face(self):
        """
        Create a simple default face using Pygame drawing
        """
        face_surface = pygame.Surface((self.screen_width, self.screen_height))
        face_surface.fill((255, 255, 255))  # White background

        # Draw basic face elements
        pygame.draw.circle(face_surface, (0, 0, 0),
                           (self.screen_width // 2, self.screen_height // 2),
                           200, 5)  # Outline

        # Eyes
        pygame.draw.circle(face_surface, (0, 0, 0),
                           (self.screen_width // 3, self.screen_height // 3),
                           30)
        pygame.draw.circle(face_surface, (0, 0, 0),
                           (2 * self.screen_width // 3, self.screen_height // 3),
                           30)

        return face_surface

    def update_expression(self, expression):
        """
        Update the robot's facial expression
        """
        if expression in self.expressions:
            self.current_expression = expression
            self.screen.blit(self.expressions[self.current_expression], (0, 0))
            pygame.display.flip()

    def nghe(self):
        """
        Nghe đầu vào từ micro và chuyển thành văn bản
        """
        self.update_expression('listening')
        with sr.Microphone() as source:
            print("Đang lắng nghe...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio, language='vi-VN')
                print(f"Bạn nói: {text}")
                self.update_expression('normal')
                return text.lower()
            except sr.UnknownValueError:
                print("Xin lỗi, tôi không nghe rõ.")
                self.update_expression('normal')
                return ""
            except sr.RequestError:
                print("Không thể kết nối dịch vụ nhận dạng giọng nói.")
                self.update_expression('normal')
                return ""
            except Exception as e:
                print(f"Lỗi: {e}")
                self.update_expression('normal')
                return ""

    def noi(self, text):
        """
        Chuyển văn bản thành giọng nói bằng Google Text-to-Speech
        """
        print(f"Trợ lý: {text}")
        try:
            # Update to speaking expression before speaking
            self.update_expression('speaking')

            tts = gTTS(text, lang='vi')
            filename = "temp.mp3"
            tts.save(filename)

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()
            os.remove(filename)

            # Return to normal expression after speaking
            self.update_expression('normal')
        except Exception as e:
            print(f"Lỗi khi phát âm: {e}")
            self.update_expression('normal')

    # ... (rest of the methods remain the same as in the original code)

    def chay(self):
        """
        Vòng lặp chính của trợ lý
        """
        self.update_expression('normal')
        self.noi("Xin chào! Hãy gọi 'Robot' để bắt đầu ra lệnh.")

        while True:
            try:
                # Handle Pygame events to keep window responsive
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return

                text = self.nghe()
                if text:
                    if "thoát" in text or "bye" in text or "dừng" in text:
                        self.noi("Tạm biệt! Hẹn gặp lại.")
                        break

                    # Kiểm tra từ khóa kích hoạt
                    if "robot" in text:
                        # Phát âm thanh xác nhận
                        self.noi("Đang nhận lệnh")
                        # Đợi và xử lý lệnh tiếp theo
                        if not self.cho_lenh():
                            break
                    else:
                        print("Đang chờ lệnh kích hoạt 'Chào Robot'...")

            except Exception as e:
                print(f"Lỗi trong quá trình chạy: {e}")
                self.noi("Đã có lỗi xảy ra. Xin hãy thử lại.")
                self.update_expression('normal')


def main():
    # Thay thế các API keys của bạn vào đây
    GEMINI_API_KEY = 'AIzaSyC5VpC4idAiZI3V6DUrCVRN1eAG2km4yJY'

    try:
        tro_ly = TroLyAo(GEMINI_API_KEY)
        tro_ly.chay()
    except Exception as e:
        print(f"Lỗi khởi động: {e}")


if __name__ == "__main__":
    main()