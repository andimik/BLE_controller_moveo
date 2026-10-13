# Moveo Fitness BLE Controller

Dieses Repository enthält ein Python-basiertes Steuerungsskript für ein **Moveo Fitnessgerät** (ca. 1500 EUR teurer Stepper mit Bluetooth-Fernbedienung). Zum Betrieb der vom Hersteller angebotenen und im Google Play Store erhältlichen App ist zwingend ein Googlekonto nötig (die App verweigert nach einigen Versuchen dauerhaft ihren Dienst, wenn man nicht bei Google angemeldet ist) und ein kostenloses Konto beim Hersteller, obwohl beides nicht nötig ist.

Die spartanische Fernbedienung (mit den Tasten Ein/Aus, Schneller und Langsamer) hat offenbar einen Software-Bug, da sie nicht verlässlich stoppt oder das Gerät erst gar nicht startet. Daher wurde dieses Skript geschrieben, das zuverlässig unter Ubuntu 25.10 getestet wurde.

Das (unverschlüsselte) Protokoll des Herstellers wurde erfolgreich via Reverse Engineering (HCI-Snoop-Logs und Bluetooth-Analyse am Android Mobiltelefon) rekonstruiert. Mit diesem Skript lässt sich das Gerät plattformübergreifend direkt über das Terminal eines Laptops oder PCs steuern.

---

## 🛑 Wichtiger Sicherheitshinweis (Disclaimer)

> [!WARNING]
> **Nutzung auf eigene Gefahr!** Dieses Projekt steht in keinerlei Verbindung zum Original-Hersteller des Geräts. Da dieses Skript ein physisches Fitnessgerät steuert, das sich mechanisch bewegt, ist höchste Vorsicht geboten. Der Autor übernimmt absolut keine Haftung für Schäden am Gerät, Unfälle, Fehlfunktionen oder Verletzungen, die durch die Nutzung oder Modifikation dieses Codes entstehen.

---

## 🔬 Das BLE-Protokoll (Technische Details)

Das Gerät meldet sich in der Bluetooth-Umgebung standardmäßig mit dem Namen **`Moveo`**. Es nutzt einen Jieli/Phyplus-Chipsatz mit einer proprietären GATT-Struktur.

* **Schreib-Charakteristik (Write Without Response):** `0000ae01-0000-1000-8000-00805f9b34fb`
* **Status-Benachrichtigungen (Notify):** `0000ae02-0000-1000-8000-00805f9b34fb`

### Extrahierte Befehlssequenzen (Hex-Payloads)

Die Steuerbefehle werden im Raw-Format als Byte-Arrays an die `ae01`-Charakteristik gesendet:

| Aktion | Hex-Payload | Beschreibung |
| :--- | :--- | :--- |
| **START** | `ae 01` | Startet den manuellen Trainingsmodus (Standard: Stufe 3) |
| **STOP** | `ae 03` | Stoppt den Motor sofort |
| **SCHNELLER** | `ae 04 aa` | Erhöht die Geschwindigkeit um 1 Stufe |
| **LANGSAMER** | `ae 05 aa` | Verringert die Geschwindigkeit um 1 Stufe |

### Status-Rückmeldungen des Geräts
Über den `ae02`-Notify-Kanal sendet das Laufband kontinuierlich seinen aktuellen Zustand. 
* Ein Paket im Format `ad 08 01 [STUFE] 03 [CHECKSUMME]` signalisiert den aktiven Betrieb. Das vierte Byte verrät dabei die exakte, aktuelle Geschwindigkeitsstufe als Hexadezimalwert.

---

## ⌨️ Tastaturbefehle im Skript

Sobald die Verbindung erfolgreich hergestellt wurde, lässt sich das Gerät interaktiv über das Terminal steuern:

* `1` + `Enter` ➡️ Motor **START**
* `2` + `Enter` ➡️ Motor **STOP**
* `+` + `Enter` ➡️ Geschwindigkeit **erhöhen** (Integrierte Softwaresperre bei Stufe 10)
* `-` + `Enter` ➡️ Geschwindigkeit **verringern** (Integrierte Softwaresperre/Underflow-Schutz bei Stufe 1)
* `h` oder `help` ➡️ Befehlsübersicht erneut anzeigen
* `q` + `Enter` ➡️ Verbindung trennen & Skript sicher **beenden**

---

## 🛠️ Installation & Einrichtung (Linux / macOS / Windows)

Das Skript basiert auf der modernen und asynchronen BLE-Bibliothek `bleak`. Da neuere Betriebssysteme (insbesondere Linux-Distributionen wie Ubuntu/Debian) globale Python-Installationen blockieren, wird die Einrichtung über eine virtuelle Umgebung empfohlen.

### 1. Voraussetzungen installieren (Beispiel für Ubuntu/Debian)

Stelle sicher, dass Python 3 und die System-Bluetooth-Bibliotheken vorhanden sind:

```bash
sudo apt update
sudo apt install -y python3-venv python3-full
```

### 2. Skript herunterladen

Einen Ordner erstellen und dorthin navigieren:

```bash
mkdir ble_controller_moveo
cd ble_controller_moveo
```

Kopiere dann hier die `moveo_ansprechen.py` aus diesem Repository.


### 3. Virtuelle Umgebung erstellen und aktivieren

```bash
python3 -m venv moveo-env
source moveo-env/bin/activate
```
*(Dein Terminal-Prompt zeigt nun ein präfixartiges `(moveo-env)` an.)*

### 4. Abhängigkeiten installieren

Installiere die benötigte Bluetooth-Bibliothek in der isolierten Umgebung:

```bash
pip install bleak
```

---

## 🚀 Skript starten

1. Schalte das Moveo-Fitnessgerät ein.
2. **Wichtig:** Stelle sicher, dass die originale Smartphone-App (Moveo) komplett geschlossen und Bluetooth am Handy temporär deaktiviert ist. BLE-Geräte erlauben meist nur eine aktive Verbindung gleichzeitig.
3. Führe das Skript aus deiner aktivierten virtuellen Umgebung heraus aus:
```bash
python moveo_ansprechen.py
```

Das Skript scannt automatisch nach dem Namen `Moveo`, zieht sich die dynamisch wechselnde MAC-Adresse (RPA-Schutz des Herstellers) und öffnet die Konsole zur Steuerung.

---

## 📜 Lizenz
Dieses Projekt ist unter der [MIT License](LICENSE) lizenziert – freie Nutzung für private Zwecke und Modifikationen zur Wahrung der Interoperabilität.

