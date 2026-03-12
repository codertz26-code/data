import os
import time
import json
from datetime import datetime
from logger import save_to_db

def get_wifi_info():
    """Inachukua taarifa za Wi-Fi kwa kutumia Termux commands"""
    
    # Angalia kama Wi-Fi imewashwa
    wifi_status = os.popen("termux-wifi-scaninfo").read()
    
    # Tafuta jina la mtandao uliounganishwa
    connection = os.popen("termux-wifi-connection").read()
    
    data = {
        'timestamp': datetime.now().isoformat(),
        'network': 'unknown',
        'data': 0,
        'signal': 'unknown',
        'extra': {}
    }
    
    try:
        # Jaribu kupata jina la mtandao
        if connection:
            conn_info = json.loads(connection)
            data['network'] = conn_info.get('ssid', 'unknown')
            data['signal'] = str(conn_info.get('rssi', 0))
    except:
        pass
    
    # Pata matumizi ya data (kupitia termux)
    usage = os.popen("termux-battery-status").read()  # Hii ni placeholder, tutatumia njia nyingine
    data['extra']['usage'] = usage[:100]  # Weka sehemu ya kwanza tu
    
    return data

def main():
    print("🚀 Mkusanyaji data ameanza...")
    print("📊 Ataandika data kwenye /sdcard/Download/data.db")
    
    while True:
        try:
            # Kukusanya data
            data = get_wifi_info()
            
            # Kuhifadhi
            save_to_db(data)
            
            # Onyesha kwenye terminal
            print(f"[✓] {data['timestamp']} - {data['network']}")
            
            # Subiri kabla ya kukusanya tena
            time.sleep(60)  # Kila dakika 1
            
        except KeyboardInterrupt:
            print("\n👋 Imekoma. Data iko salama!")
            break
        except Exception as e:
            print(f"❌ Kosa: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
