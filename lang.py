"""
Farmer-facing text in English, Hindi, Marathi and Kannada.
English is the default. Only the Advisor screen is translated.
"""
LANGUAGES = {"English": "en", "हिंदी (Hindi)": "hi", "मराठी (Marathi)": "mr", "ಕನ್ನಡ (Kannada)": "kn"}

T = {
    "en": {
        "head_ok": "Soil moisture is fine for now.",
        "head_need": "Your field needs water.",
        "head_stress": "Your crop is short of water. Water it as soon as possible.",
        "act": "Run the pump {when}, from {start}, for {hours} hours.",
        "act_split": "Run the pump {when}, from {start}: {hours} hours in total, split over {n} nights.",
        "act_rain": "Rain is coming. No need to water this week.",
        "act_none": "No watering needed for the next 7 days.",
        "when0": "tonight", "when1": "tomorrow night", "whenN": "on the night of {date}",
        "why_water": "Soil moisture is {m}%. Give about {mm} mm of water. Electricity is available {window}.",
        "why_none": "Soil moisture is {m}%.",
        "window": "{a} to {b}",
        "m_moist": "Soil moisture now", "m_water": "Water to give", "m_pump": "Pump time", "hours": "hours",
        "rain_exp": "Rain forecast for the next 7 days (mm)",
        "rain_live": "Filled in from the live weather forecast for your village. You can change any value.",
        "rain_off": "Live forecast not available. Type the rain expected each day (from IMD or a weather app).",
        "tonight": "Tonight → ",
        "chart": "Soil moisture: next 7 days", "y": "Soil moisture (%)",
        "z_good": "Good", "z_soon": "Water soon", "z_danger": "Danger",
        "l_past": "Past days", "l_plan": "If you follow the advice", "l_none": "If you don't water",
        "risk_title": "What if you wait?",
        "risk_safe": "If you follow this advice, your crop stays safe.",
        "risk_some": "Even with this advice there is a small risk ({p}%) of water stress.",
        "risk_none": "If you don't water at all, there is a {p}% chance your crop suffers.",
        "slider": "If I wait this many days before watering:",
        "risk_delay": "Waiting {d} days: {p}% chance of water stress, about {y}% less harvest.",
        "risk_delay0": "Move the slider to see what happens if you wait.",
        "dec": "Your decision", "yes": "✔ I will water", "no": "✖ Not today",
        "said_yes": "You said: I will water", "said_no": "You said: Not today",
        "fert": "Fertilizer tip:",
        "fert_yes": "Mix fertilizer only in the middle part of the pump run. Run plain water at the start and at "
                    "the end, so the fertilizer stays near the roots.",
        "fert_no": "No fertilizer this week. Give fertilizer only together with watering.",
    },
    "hi": {
        "head_ok": "अभी मिट्टी में नमी ठीक है।",
        "head_need": "आपके खेत को पानी चाहिए।",
        "head_stress": "आपकी फसल में पानी की कमी है। जल्द से जल्द पानी दें।",
        "act": "{when} पंप चलाएँ — {start} बजे से {hours} घंटे।",
        "act_split": "{when} पंप चलाएँ — {start} बजे से, कुल {hours} घंटे, {n} रातों में बाँटकर।",
        "act_rain": "बारिश आने वाली है। इस हफ्ते पानी देने की ज़रूरत नहीं है।",
        "act_none": "अगले 7 दिन पानी देने की ज़रूरत नहीं है।",
        "when0": "आज रात", "when1": "कल रात", "whenN": "{date} की रात",
        "why_water": "मिट्टी की नमी {m}% है। लगभग {mm} मिमी पानी दें। बिजली {window} रहती है।",
        "why_none": "मिट्टी की नमी {m}% है।",
        "window": "{a} बजे से {b} बजे तक",
        "m_moist": "अभी मिट्टी की नमी", "m_water": "कितना पानी दें", "m_pump": "पंप का समय", "hours": "घंटे",
        "rain_exp": "अगले 7 दिन की बारिश का अनुमान (मिमी)",
        "rain_live": "आपके गाँव के मौसम पूर्वानुमान से भरा गया है। आप कोई भी संख्या बदल सकते हैं।",
        "rain_off": "मौसम पूर्वानुमान उपलब्ध नहीं है। हर दिन की संभावित बारिश (IMD या मौसम ऐप से) लिखें।",
        "tonight": "आज रात → ",
        "chart": "मिट्टी की नमी: अगले 7 दिन", "y": "मिट्टी की नमी (%)",
        "z_good": "ठीक", "z_soon": "जल्द पानी दें", "z_danger": "खतरा",
        "l_past": "पिछले दिन", "l_plan": "सलाह मानने पर", "l_none": "पानी न देने पर",
        "risk_title": "अगर आप रुकें तो क्या होगा?",
        "risk_safe": "यह सलाह मानने पर आपकी फसल सुरक्षित रहेगी।",
        "risk_some": "सलाह मानने पर भी पानी की कमी का थोड़ा खतरा ({p}%) है।",
        "risk_none": "अगर आप पानी बिल्कुल नहीं देते, तो फसल को नुकसान की संभावना {p}% है।",
        "slider": "अगर मैं इतने दिन रुकूँ:",
        "risk_delay": "{d} दिन रुकने पर: पानी की कमी की संभावना {p}%, फसल लगभग {y}% कम।",
        "risk_delay0": "रुकने का असर देखने के लिए स्लाइडर खिसकाएँ।",
        "dec": "आपका फैसला", "yes": "✔ मैं पानी दूँगा", "no": "✖ आज नहीं",
        "said_yes": "आपने कहा: मैं पानी दूँगा", "said_no": "आपने कहा: आज नहीं",
        "fert": "खाद सलाह:",
        "fert_yes": "खाद केवल पंप चलने के बीच वाले समय में मिलाएँ। शुरू और आखिर में सिर्फ पानी चलाएँ, "
                    "ताकि खाद जड़ों के पास रहे।",
        "fert_no": "इस हफ्ते खाद नहीं। खाद हमेशा पानी के साथ ही दें।",
    },
    "mr": {
        "head_ok": "सध्या मातीतील ओलावा ठीक आहे.",
        "head_need": "तुमच्या शेताला पाणी हवे आहे.",
        "head_stress": "तुमच्या पिकाला पाण्याची कमतरता आहे. लवकरात लवकर पाणी द्या.",
        "act": "{when} पंप चालू करा — {start} वाजल्यापासून {hours} तास.",
        "act_split": "{when} पंप चालू करा — {start} वाजल्यापासून, एकूण {hours} तास, {n} रात्रींमध्ये विभागून.",
        "act_rain": "पाऊस येणार आहे. या आठवड्यात पाणी देण्याची गरज नाही.",
        "act_none": "पुढील 7 दिवस पाणी देण्याची गरज नाही.",
        "when0": "आज रात्री", "when1": "उद्या रात्री", "whenN": "{date} रोजी रात्री",
        "why_water": "मातीतील ओलावा {m}% आहे. सुमारे {mm} मिमी पाणी द्या. वीज {window} असते.",
        "why_none": "मातीतील ओलावा {m}% आहे.",
        "window": "{a} ते {b}",
        "m_moist": "सध्याचा ओलावा", "m_water": "किती पाणी द्यावे", "m_pump": "पंपाचा वेळ", "hours": "तास",
        "rain_exp": "पुढील 7 दिवसांचा पावसाचा अंदाज (मिमी)",
        "rain_live": "तुमच्या गावाच्या हवामान अंदाजावरून भरले आहे. तुम्ही कोणताही आकडा बदलू शकता.",
        "rain_off": "हवामान अंदाज उपलब्ध नाही. दररोज अपेक्षित पाऊस (IMD किंवा हवामान ॲपवरून) लिहा.",
        "tonight": "आज रात्री → ",
        "chart": "मातीतील ओलावा: पुढील 7 दिवस", "y": "मातीतील ओलावा (%)",
        "z_good": "ठीक", "z_soon": "लवकर पाणी द्या", "z_danger": "धोका",
        "l_past": "मागील दिवस", "l_plan": "सल्ला पाळल्यास", "l_none": "पाणी न दिल्यास",
        "risk_title": "थांबल्यास काय होईल?",
        "risk_safe": "हा सल्ला पाळल्यास तुमचे पीक सुरक्षित राहील.",
        "risk_some": "सल्ला पाळूनही पाण्याच्या कमतरतेचा थोडा धोका ({p}%) आहे.",
        "risk_none": "अजिबात पाणी न दिल्यास पिकाचे नुकसान होण्याची शक्यता {p}% आहे.",
        "slider": "मी इतके दिवस थांबलो तर:",
        "risk_delay": "{d} दिवस थांबल्यास: पाण्याच्या कमतरतेची शक्यता {p}%, उत्पादन सुमारे {y}% कमी.",
        "risk_delay0": "थांबण्याचा परिणाम पाहण्यासाठी स्लायडर हलवा.",
        "dec": "तुमचा निर्णय", "yes": "✔ मी पाणी देईन", "no": "✖ आज नाही",
        "said_yes": "तुम्ही म्हणालात: मी पाणी देईन", "said_no": "तुम्ही म्हणालात: आज नाही",
        "fert": "खत सल्ला:",
        "fert_yes": "खत फक्त पंप चालण्याच्या मधल्या वेळेत मिसळा. सुरुवातीला आणि शेवटी फक्त पाणी द्या, "
                    "म्हणजे खत मुळांजवळ राहील.",
        "fert_no": "या आठवड्यात खत नाही. खत नेहमी पाण्यासोबतच द्या.",
    },
    "kn": {
        "head_ok": "ಸದ್ಯಕ್ಕೆ ಮಣ್ಣಿನ ತೇವಾಂಶ ಸರಿಯಾಗಿದೆ.",
        "head_need": "ನಿಮ್ಮ ಹೊಲಕ್ಕೆ ನೀರು ಬೇಕು.",
        "head_stress": "ನಿಮ್ಮ ಬೆಳೆಗೆ ನೀರಿನ ಕೊರತೆ ಇದೆ. ಆದಷ್ಟು ಬೇಗ ನೀರು ಕೊಡಿ.",
        "act": "{when} ಪಂಪ್ ಚಾಲೂ ಮಾಡಿ — {start} ಗಂಟೆಯಿಂದ {hours} ಗಂಟೆ.",
        "act_split": "{when} ಪಂಪ್ ಚಾಲೂ ಮಾಡಿ — {start} ಗಂಟೆಯಿಂದ, ಒಟ್ಟು {hours} ಗಂಟೆ, {n} ರಾತ್ರಿಗಳಲ್ಲಿ ಹಂಚಿ.",
        "act_rain": "ಮಳೆ ಬರಲಿದೆ. ಈ ವಾರ ನೀರು ಕೊಡುವ ಅಗತ್ಯವಿಲ್ಲ.",
        "act_none": "ಮುಂದಿನ 7 ದಿನ ನೀರು ಕೊಡುವ ಅಗತ್ಯವಿಲ್ಲ.",
        "when0": "ಇಂದು ರಾತ್ರಿ", "when1": "ನಾಳೆ ರಾತ್ರಿ", "whenN": "{date} ರಾತ್ರಿ",
        "why_water": "ಮಣ್ಣಿನ ತೇವಾಂಶ {m}% ಇದೆ. ಸುಮಾರು {mm} ಮಿ.ಮೀ. ನೀರು ಕೊಡಿ. ವಿದ್ಯುತ್ {window} ಇರುತ್ತದೆ.",
        "why_none": "ಮಣ್ಣಿನ ತೇವಾಂಶ {m}% ಇದೆ.",
        "window": "{a} ರಿಂದ {b} ರವರೆಗೆ",
        "m_moist": "ಈಗಿನ ತೇವಾಂಶ", "m_water": "ಎಷ್ಟು ನೀರು ಕೊಡಬೇಕು", "m_pump": "ಪಂಪ್ ಸಮಯ", "hours": "ಗಂಟೆ",
        "rain_exp": "ಮುಂದಿನ 7 ದಿನಗಳ ಮಳೆ ಮುನ್ಸೂಚನೆ (ಮಿ.ಮೀ.)",
        "rain_live": "ನಿಮ್ಮ ಊರಿನ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆಯಿಂದ ತುಂಬಲಾಗಿದೆ. ನೀವು ಯಾವುದೇ ಸಂಖ್ಯೆಯನ್ನು ಬದಲಾಯಿಸಬಹುದು.",
        "rain_off": "ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ ಲಭ್ಯವಿಲ್ಲ. ಪ್ರತಿದಿನದ ನಿರೀಕ್ಷಿತ ಮಳೆಯನ್ನು (IMD ಅಥವಾ ಹವಾಮಾನ ಆ್ಯಪ್‌ನಿಂದ) ಬರೆಯಿರಿ.",
        "tonight": "ಇಂದು ರಾತ್ರಿ → ",
        "chart": "ಮಣ್ಣಿನ ತೇವಾಂಶ: ಮುಂದಿನ 7 ದಿನ", "y": "ಮಣ್ಣಿನ ತೇವಾಂಶ (%)",
        "z_good": "ಸರಿ", "z_soon": "ಬೇಗ ನೀರು ಕೊಡಿ", "z_danger": "ಅಪಾಯ",
        "l_past": "ಹಿಂದಿನ ದಿನಗಳು", "l_plan": "ಸಲಹೆ ಪಾಲಿಸಿದರೆ", "l_none": "ನೀರು ಕೊಡದಿದ್ದರೆ",
        "risk_title": "ಕಾಯ್ದರೆ ಏನಾಗುತ್ತದೆ?",
        "risk_safe": "ಈ ಸಲಹೆ ಪಾಲಿಸಿದರೆ ನಿಮ್ಮ ಬೆಳೆ ಸುರಕ್ಷಿತವಾಗಿರುತ್ತದೆ.",
        "risk_some": "ಸಲಹೆ ಪಾಲಿಸಿದರೂ ನೀರಿನ ಕೊರತೆಯ ಸ್ವಲ್ಪ ಅಪಾಯ ({p}%) ಇದೆ.",
        "risk_none": "ನೀರು ಕೊಡದಿದ್ದರೆ ಬೆಳೆಗೆ ಹಾನಿಯಾಗುವ ಸಾಧ್ಯತೆ {p}%.",
        "slider": "ನಾನು ಇಷ್ಟು ದಿನ ಕಾಯ್ದರೆ:",
        "risk_delay": "{d} ದಿನ ಕಾಯ್ದರೆ: ನೀರಿನ ಕೊರತೆಯ ಸಾಧ್ಯತೆ {p}%, ಇಳುವರಿ ಸುಮಾರು {y}% ಕಡಿಮೆ.",
        "risk_delay0": "ಕಾಯುವುದರ ಪರಿಣಾಮ ನೋಡಲು ಸ್ಲೈಡರ್ ಸರಿಸಿ.",
        "dec": "ನಿಮ್ಮ ನಿರ್ಧಾರ", "yes": "✔ ನಾನು ನೀರು ಕೊಡುತ್ತೇನೆ", "no": "✖ ಇಂದು ಬೇಡ",
        "said_yes": "ನೀವು ಹೇಳಿದ್ದು: ನಾನು ನೀರು ಕೊಡುತ್ತೇನೆ", "said_no": "ನೀವು ಹೇಳಿದ್ದು: ಇಂದು ಬೇಡ",
        "fert": "ಗೊಬ್ಬರ ಸಲಹೆ:",
        "fert_yes": "ಪಂಪ್ ಓಡುವ ಮಧ್ಯದ ಸಮಯದಲ್ಲಿ ಮಾತ್ರ ಗೊಬ್ಬರ ಬೆರೆಸಿ. ಆರಂಭ ಮತ್ತು ಕೊನೆಯಲ್ಲಿ ಕೇವಲ ನೀರು ಕೊಡಿ, "
                    "ಆಗ ಗೊಬ್ಬರ ಬೇರುಗಳ ಹತ್ತಿರ ಇರುತ್ತದೆ.",
        "fert_no": "ಈ ವಾರ ಗೊಬ್ಬರ ಬೇಡ. ಗೊಬ್ಬರವನ್ನು ಯಾವಾಗಲೂ ನೀರಿನ ಜೊತೆಗೆ ಕೊಡಿ.",
    },
}

# time-of-day words used before the clock hour (e.g. "रात 10")
_PART = {"hi": ("रात", "सुबह", "दोपहर", "शाम"), "mr": ("रात्री", "सकाळी", "दुपारी", "संध्याकाळी"),
         "kn": ("ರಾತ್ರಿ", "ಬೆಳಿಗ್ಗೆ", "ಮಧ್ಯಾಹ್ನ", "ಸಂಜೆ")}


def hour(h: int, lg: str) -> str:
    h %= 24
    h12 = h % 12 or 12
    if lg == "en":
        return f"{h12} {'AM' if h < 12 else 'PM'}"
    night, morning, noon, evening = _PART[lg]
    part = night if (h >= 20 or h < 5) else morning if h < 12 else noon if h < 17 else evening
    return f"{part} {h12}"


def day(ts, lg: str) -> str:
    return ts.strftime("%a %d %b") if lg == "en" else ts.strftime("%d/%m")
