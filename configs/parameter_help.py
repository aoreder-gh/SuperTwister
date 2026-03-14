# ==============================================================
# Super Twister 3001
# Parameter Help Texts
# Separate help file for Config Editor
# @author    Andreas Reder <aoreder@gmail.com>
# look at validation.py for param definitions and allowed values
# ==============================================================

HELP_TEXTS = {

    # ==========================================================
    # SERVICE PARAMETERS
    # ==========================================================

    "DEBUG": {
        "DE": "Aktiviert Debug-Ausgaben auf der Konsole.\nNur für Service-Zwecke verwenden.",
        "EN": "Enables console debug output.\nFor service purposes only."
    },

    "FULLSCREEN": {
        "DE": "Startet die Anwendung im Vollbildmodus.\nBei Aktivierung werden Breite und Höhe ignoriert.",
        "EN": "Starts application in fullscreen mode.\nWidth and height values are ignored when enabled."
    },

    "width": {
        "DE": "Fensterbreite in Pixel.\nNur wirksam wenn FULLSCREEN deaktiviert ist.",
        "EN": "Application width in pixels.\nOnly active when FULLSCREEN is disabled."
    },

    "height": {
        "DE": "Fensterhöhe in Pixel.\nNur wirksam wenn FULLSCREEN deaktiviert ist.",
        "EN": "Application height in pixels.\nOnly active when FULLSCREEN is disabled."
    },

    "UPDATE_MS": {
        "DE": "Aktualisierungsintervall der Hauptschleife in Millisekunden.\nKleinere Werte erhöhen CPU-Last.",
        "EN": "Main loop update interval in milliseconds.\nLower values increase CPU load."
    },

    "MICROSTEPS": {
        "DE": "Schritte pro Umdrehung des Motors.\nAbhängig vom Stepper-Treiber (z. B. 200, 400, 800, 1600).",
        "EN": "Motor steps per revolution.\nDepends on stepper driver (e.g. 200, 400, 800, 1600)."
    },

    "PWM_DUTY": {
        "DE": "PWM-Duty-Cycle zur Ansteuerung des Motors.\nBeeinflusst Pulsbreite und Frequenz.",
        "EN": "PWM duty cycle for motor control.\nDefines pulse width and frequency."
    },

    "ENCODER_TIME": {
        "DE": "Zeitfenster für Encoder-Messung in Sekunden.\nStandardwert: 60 Sekunden.",
        "EN": "Time window for encoder measurement in seconds.\nDefault: 60 seconds."
    },

    "SLEEP_TIME": {
        "DE": "Interne Verzögerung zur Frequenzstabilisierung.\nNur bei Feintuning ändern.",
        "EN": "Internal delay for frequency stabilization.\nAdjust only for fine tuning."
    },

    "DIR_RIGHT": {
        "DE": "Definiert die Drehrichtung des Motors. Hier kann die Drehrichtung umgekehrt werden, falls die Motoren nicht korrekt laufen.\nRight = Standardrichtung.\nLeft = Invertiert.",
        "EN": "Defines motor rotation direction. Here the rotation direction can be inverted if the motors do not run correctly.\nRight = default direction.\nLeft = inverted."
    },

    "TWIST_MODE": {
        "DE": "Definiert die Drehrichtung beider Motoren wenn die Twist-Funktion aktiv ist. Hier kann die Drehrichtung umgekehrt werden, falls die Motoren nicht korrekt laufen.\nRight = Standardrichtung.\nLeft = Invertiert.",
        "EN": "Defines motors rotation direction when twist function is active. Here the rotation direction can be inverted if the motors do not run correctly.\nRight = default direction.\nLeft = inverted."
    },

    "THROTTLE_START": {
        "DE": "Start-Schwellwert in Prozent.\nMotor beginnt ab diesem Leistungswert zu laufen.",
        "EN": "Throttle start percentage.\nMotor begins running at this power level."
    },

    "ACCEL_FAST": {
        "DE": "Normale Beschleunigung.\nSollte größer als ACCEL_SLOW sein.",
        "EN": "Normal acceleration.\nShould be greater than ACCEL_SLOW."
    },

    "ACCEL_SLOW": {
        "DE": "Reduzierte Beschleunigung im Resonanzbereich.\nSollte kleiner als ACCEL_FAST sein.",
        "EN": "Reduced acceleration in resonance range.\nShould be lower than ACCEL_FAST."
    },

    "DECEL_FAST": {
        "DE": "Normale Verzögerung beim Abbremsen.",
        "EN": "Normal deceleration when stopping."
    },

    "DECEL_SLOW": {
        "DE": "Reduzierte Verzögerung im Resonanzbereich.",
        "EN": "Reduced deceleration in resonance range."
    },

    "RESONANCE_MIN": {
        "DE": "Unterer Drehzahlbereich der Resonanzzone.\nMuss kleiner als RESONANCE_MAX sein.",
        "EN": "Lower RPM threshold of resonance zone.\nMust be lower than RESONANCE_MAX."
    },

    "RESONANCE_MAX": {
        "DE": "Oberer Drehzahlbereich der Resonanzzone.",
        "EN": "Upper RPM threshold of resonance zone."
    },


    # ==========================================================
    # OPERATOR PARAMETERS
    # ==========================================================

    "DEFAULT_PROFILE": {
        "DE": "Standardprofil beim Start.\nMaximal 20 Zeichen.",
        "EN": "Default profile loaded at startup.\nMaximum 20 characters."
    },

    "RAMP_TIME": {
        "DE": "Zeit in Sekunden für Hochlauf auf Ziel-Drehzahl.",
        "EN": "Time in seconds to ramp up to target RPM."
    },

    "STOP_RAMP_TIME": {
        "DE": "Zeit in Sekunden für kontrolliertes Abbremsen.",
        "EN": "Time in seconds for controlled ramp-down."
    },

    "STOP_HARD_RPM_THRESHOLD": {
        "DE": "Drehzahl-Schwelle für sofortiges Stoppen.",
        "EN": "RPM threshold for immediate stop."
    },

    "PWM_UPDATE_THRESHOLD": {
        "DE": "Schwelle für PWM-Aktualisierung.\nBeeinflusst Rampensteuerung.",
        "EN": "Threshold for PWM update.\nAffects ramp behavior."
    },

    "MAX_TWIST": {
        "DE": "Maximal erlaubte Drehzahl für Twist-Modus.",
        "EN": "Maximum allowed RPM for twist mode."
    },

    "START_RPM": {
        "DE": "Schnellstart-Drehzahl für Initialisierung.",
        "EN": "Quick start RPM for initialization."
    },

    "CENTER_RPM": {
        "DE": "Drehzahl für Zentriervorgang.",
        "EN": "RPM used during centering procedure."
    },

    "CENTER_OFFSET_STEPS": {
        "DE": "Feinjustierung der Mittelposition.\nBereich: ± MICROSTEPS.",
        "EN": "Fine adjustment of center position.\nRange: ± MICROSTEPS."
    },

    "MIN_RPM": {
        "DE": "Minimale Motordrehzahl.\nMuss kleiner als MAX_RPM sein.",
        "EN": "Minimum motor speed.\nMust be lower than MAX_RPM."
    },

    "MAX_RPM": {
        "DE": "Maximale Motordrehzahl.\nMuss größer als MIN_RPM sein.",
        "EN": "Maximum motor speed.\nMust be greater than MIN_RPM."
    },

    "STEP_RPM": {
        "DE": "Normale Schrittweite für Drehzahlanpassung.\nSollte kleiner als FAST_STEP sein.",
        "EN": "Standard RPM step size.\nShould be lower than FAST_STEP."
    },

    "FAST_STEP": {
        "DE": "Große Schrittweite für schnelle Anpassung.",
        "EN": "Large RPM step size for quick adjustment."
    }

}