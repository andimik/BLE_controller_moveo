import asyncio
import sys
from bleak import BleakScanner, BleakClient

TARGET_NAME = "Moveo"
UUID_AE01 = "0000ae01-0000-1000-8000-00805f9b34fb"
NOTIFY_AE02 = "0000ae02-0000-1000-8000-00805f9b34fb"

# Die Steuerbefehle
CMD_START  = bytes([0xae, 0x01])
CMD_STOP   = bytes([0xae, 0x03])
CMD_FASTER = bytes([0xae, 0x04, 0xaa])
CMD_SLOWER = bytes([0xae, 0x05, 0xaa])

# Globale Variable, um die aktuelle Stufe im Skript zu tracken
current_speed_level = 0  # 0 bedeutet Motor ist aus

def print_help_menu():
    print("\n==================================================")
    print(" MOVEO BLE-STEUERUNG BEFEHLSÜBERSICHT")
    print("==================================================")
    print(" [1] -> Motor START")
    print(" [2] -> Motor STOP")
    print(" [+] -> SCHNELLER (Sperre bei Stufe 10)")
    print(" [-] -> LANGSAMER (Sperre bei Stufe 1)")
    print(" [h] oder [help] -> Diese Hilfe anzeigen")
    print(" [q] -> Verbindung TRENNEN & BEENDEN")
    print("==================================================\n")

def status_notification_handler(sender, data):
    global current_speed_level
    hex_data = data.hex()
    
    if len(hex_data) >= 12 and hex_data.startswith("ad08"):
        new_level = int(hex_data[6:8], 16)
        if new_level != current_speed_level:
            current_speed_level = new_level
        print(f"\r[Moveo Status] Motor läuft | Aktuelle Stufe: {current_speed_level}     ", end="", flush=True)
    elif hex_data == "ad0801000384":
        current_speed_level = 0
        print("\r[Moveo Status] Standby / Motor AUS                                 ", end="", flush=True)

async def user_input_loop(client):
    global current_speed_level
    print_help_menu()

    loop = asyncio.get_event_loop()
    
    while True:
        user_choice = await loop.run_in_executor(None, lambda: sys.stdin.readline().strip())
        
        if not user_choice:
            continue
            
        if user_choice == "1":
            print("\nSende: START...")
            await client.write_gatt_char(UUID_AE01, CMD_START, response=False)
            
        elif user_choice == "2":
            print("\nSende: STOP...")
            await client.write_gatt_char(UUID_AE01, CMD_STOP, response=False)
            
        elif user_choice == "+":
            if current_speed_level < 10:
                print("\nSende: SCHNELLER...")
                await client.write_gatt_char(UUID_AE01, CMD_FASTER, response=False)
            else:
                print("\n[Sicherheit] Maximale Stufe 10 bereits erreicht! Befehl blockiert.")
                
        elif user_choice == "-":
            if current_speed_level > 1:
                print("\nSende: LANGSAMER...")
                await client.write_gatt_char(UUID_AE01, CMD_SLOWER, response=False)
            elif current_speed_level == 1:
                print("\n[Sicherheit] Geringste Stufe 1 bereits erreicht! Underflow-Schutz aktiv.")
            else:
                print("\nMotor läuft aktuell nicht. Befehl ignoriert.")
                
        elif user_choice.lower() in ["h", "help"]:
            print_help_menu()
            # Zeigt den aktuellen Status direkt nach dem Menü wieder an, falls der Motor läuft
            if current_speed_level > 0:
                print(f"[Moveo Status] Motor läuft | Aktuelle Stufe: {current_speed_level}     ", end="", flush=True)
            else:
                print("[Moveo Status] Standby / Motor AUS                                 ", end="", flush=True)

        elif user_choice.lower() == "q":
            print("\nBeende Steuerung und trenne Bluetooth...")
            await client.write_gatt_char(UUID_AE01, CMD_STOP, response=False)
            break
        else:
            print(f"\nUnbekannter Befehl: '{user_choice}' (Tippe 'h' für Hilfe)")

async def main():
    print(f"Suche nach '{TARGET_NAME}'...")
    device = await BleakScanner.find_device_by_filter(
        lambda d, a: d.name == TARGET_NAME, timeout=10.0
    )
    if not device:
        print("Gerät nicht gefunden.")
        return
        
    print(f"Gefunden! Verbinde mit {device.address}...")
    async with BleakClient(device) as client:
        if client.is_connected:
            print("Erfolgreich verbunden!")
            await client.start_notify(NOTIFY_AE02, status_notification_handler)
            await asyncio.sleep(0.5)
            await user_input_loop(client)
            await client.stop_notify(NOTIFY_AE02)
            print("Verbindung sauber getrennt.")

if __name__ == "__main__":
    asyncio.run(main())
