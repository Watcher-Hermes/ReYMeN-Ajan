# -*- coding: utf-8 -*-
"""
araclar_ses.py — Sesli komut girişi.
Mikrofonu dinler, konuşmayı metne çevirir ("yeni projeye başlıyoruz" gibi).

Bağımlılık: SpeechRecognition + pyaudio. Opsiyonel.
    pip install SpeechRecognition pyaudio
Google'ın ücretsiz tanıma servisini kullanır (internet gerekir) veya
çevrimdışı için Vosk eklenebilir.
"""
try:
    import speech_recognition as sr
    SR_OK = True
except Exception:
    SR_OK = False


class SesliKomut:
    def __init__(self, dil="tr-TR"):
        self.dil = dil
        self._recognizer = sr.Recognizer() if SR_OK else None

    def dinle(self, zaman_asimi=5):
        """Mikrofondan tek bir komut dinler, metne çevirir."""
        if not SR_OK:
            return "[Ses]: SpeechRecognition kurulu değil (pip install SpeechRecognition pyaudio)."
        try:
            with sr.Microphone() as kaynak:
                self._recognizer.adjust_for_ambient_noise(kaynak, duration=0.5)
                print("[Ses]: Dinliyorum...")
                ses = self._recognizer.listen(kaynak, timeout=zaman_asimi)
            metin = self._recognizer.recognize_google(ses, language=self.dil)
            return metin
        except sr.WaitTimeoutError:
            return "[Ses]: Zaman aşımı, ses algılanmadı."
        except sr.UnknownValueError:
            return "[Ses]: Ne dediğiniz anlaşılamadı."
        except Exception as e:
            return f"[Ses Hatası]: {e}"

    def seslendir(self, metin):
        """Metni seslendirir (TTS). pyttsx3 kurulu degilse graceful degrade."""
        try:
            import pyttsx3
            motor = pyttsx3.init()
            motor.say(metin)
            motor.runAndWait()
            return "[Ses]: Seslendirildi."
        except ImportError:
            return "[Ses]: TTS kurulu degil (pip install pyttsx3)."
        except Exception as e:
            return f"[Ses Hatasi]: {e}"

    def komut_bekle(self, tetikleyici="yeni proje"):
        """Belirli bir tetikleyici cümle duyana kadar dinler (basit eşleşme)."""
        metin = self.dinle()
        if isinstance(metin, str) and tetikleyici.lower() in metin.lower():
            return {"tetiklendi": True, "metin": metin}
        return {"tetiklendi": False, "metin": metin}


def motor_kaydet(motor):
    """Ses araçlarını motora kaydet."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    _sk = SesliKomut()
    motor._plugin_arac_kaydet(
        "SES_DINLE",
        lambda: _sk.dinle(),
        "Mikrofondan sesli komut dinle ve metne çevir",
    )


if __name__ == "__main__":
    s = SesliKomut()
    print("SesliKomut hazir (SpeechRecognition:%s)" % SR_OK)
