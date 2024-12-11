import speech_recognition as sr
from gtts import gTTS
import os
import datetime
import webbrowser
import pygame
import google.generativeai as genai


class TroLyAo:
    def __init__(self, api_key):
        self.recognizer = sr.Recognizer()
        pygame.mixer.init()
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def nghe(self):
        """
        Nghe đầu vào từ micro và chuyển thành văn bản
        """
        with sr.Microphone() as source:
            print("Đang lắng nghe...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio, language='vi-VN')
                print(f"Bạn nói: {text}")
                return text.lower()
            except sr.UnknownValueError:
                print("Xin lỗi, tôi không nghe rõ.")
                return ""
            except sr.RequestError:
                print("Không thể kết nối dịch vụ nhận dạng giọng nói.")
                return ""
            except Exception as e:
                print(f"Lỗi: {e}")
                return ""

    def noi(self, text):
        """
        Chuyển văn bản thành giọng nói bằng Google Text-to-Speech
        """
        print(f"Trợ lý: {text}")
        try:
            tts = gTTS(text, lang='vi')
            filename = "temp.mp3"
            tts.save(filename)

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()
            os.remove(filename)
        except Exception as e:
            print(f"Lỗi khi phát âm: {e}")

    def rut_gon_van_ban(self, van_ban, max_tokens=100):
        """
        Rút gọn văn bản theo số lượng từ
        """
        cac_tu = van_ban.split()
        if len(cac_tu) <= max_tokens:
            return van_ban
        rut_gon = ' '.join(cac_tu[:max_tokens]) + '...'
        return rut_gon

    def tra_loi_tu_gemini(self, cau_hoi, max_tokens=100):
        """
        Sử dụng Gemini AI để trả lời câu hỏi với giới hạn token
        """
        try:
            prompt = f"{cau_hoi}. Trả lời ngắn gọn và rõ ràng."
            response = self.model.generate_content(prompt)
            tra_loi_rut_gon = self.rut_gon_van_ban(response.text, max_tokens)
            return tra_loi_rut_gon
        except Exception as e:
            print(f"Lỗi khi truy vấn Gemini: {e}")
            return "Xin lỗi, tôi gặp khó khăn trong việc trả lời câu hỏi của bạn."

    def xu_ly_lenh(self, lenh):
        """
        Xử lý các lệnh giọng nói
        """
        try:
            if "mấy giờ" in lenh or "giờ" in lenh:
                thoi_gian_hien_tai = datetime.datetime.now()
                gio_format = f"Bây giờ là {thoi_gian_hien_tai.hour} giờ {thoi_gian_hien_tai.minute} phút, ngày {thoi_gian_hien_tai.day} tháng {thoi_gian_hien_tai.month}"
                self.noi(gio_format)

            elif "bạn là ai" in lenh:
                self.noi("Tôi là MBot, Robot hỗ trợ theo dõi")
            elif "chức năng gì" in lenh:
                self.noi(
                    "Tôi có chức năng hỗ trợ theo dõi, cảnh báo cho người lớn tuổi hoặc trẻ nhỏ khi ở nhà một mình, tránh khỏi các tác nhân nguy hiểm")
            elif "mở trình duyệt" in lenh:
                webbrowser.open("https://www.google.com.vn")
                self.noi("Đang mở trình duyệt Google")
            elif "xin chào" in lenh or "hello" in lenh:
                self.noi("Xin chào! Tôi là trợ lý ảo. Bạn cần giúp gì?")
            elif "hôm nay" in lenh:
                ngay_hien_tai = datetime.datetime.now()
                ngay_format = f"Hôm nay là {ngay_hien_tai.day} tháng {ngay_hien_tai.month} năm {ngay_hien_tai.year}"
                self.noi(ngay_format)
            elif lenh.strip():  # Nếu còn lệnh khác không rỗng
                tra_loi = self.tra_loi_tu_gemini(lenh, max_tokens=50)
                self.noi(tra_loi)

        except Exception as e:
            self.noi(f"Đã có lỗi xảy ra: {str(e)}")

    def cho_lenh(self):
        """
        Đợi và xử lý lệnh từ người dùng
        """
        lenh = self.nghe()
        if lenh:
            if "thoát" in lenh or "bye" in lenh or "dừng" in lenh:
                self.noi("Tạm biệt! Hẹn gặp lại.")
                return False
            self.xu_ly_lenh(lenh)
        return True

    def chay(self):
        """
        Vòng lặp chính của trợ lý
        """
        self.noi("Xin chào! Hãy gọi 'Chào MBot' để bắt đầu ra lệnh.")

        while True:
            try:
                text = self.nghe()
                if text:
                    if "thoát" in text or "bye" in text or "dừng" in text:
                        self.noi("Tạm biệt! Hẹn gặp lại.")
                        break

                    # Kiểm tra từ khóa kích hoạt
                    if "chào robot" in text:
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


def main():
    API_KEY = 'AIzaSyC5VpC4idAiZI3V6DUrCVRN1eAG2km4yJY'

    try:
        tro_ly = TroLyAo(API_KEY)
        tro_ly.chay()
    except Exception as e:
        print(f"Lỗi khởi động: {e}")


if __name__ == "__main__":
    main()