# -*- coding: utf-8 -*-
"""
knowledge_base.py — basis pengetahuan gejala-penyakit untuk BINUS Disease
Detection.

PENTING (baca ini dulu): data di file ini adalah representasi SEDERHANA dan
UMUM dari pola gejala yang biasa diajarkan di edukasi kesehatan dasar —
bukan basis data medis klinis, dan sengaja TIDAK menyertakan info dosis
obat atau protokol pengobatan apapun. Aplikasi ini murni alat skrining
edukatif untuk portofolio, bukan alat diagnosis medis. Selalu arahkan
pengguna ke tenaga medis profesional untuk diagnosis & penanganan yang
sesungguhnya — ini ditegakkan di lapisan API (api.py) dan UI (web),
bukan cuma di sini.

CATATAN SOAL FITUR TAMBAHAN (BMI, tensi, durasi sakit):
- "duration_typical" menandai apakah kondisi ini KHAS akut (hitungan hari),
  subakut (1-4 minggu), kronis (berbulan-bulan), atau "bervariasi" (tidak
  ada pola waktu yang khas). Ini dipetakan jadi distribusi probabilitas di
  DURATION_ARCHETYPES, dipakai untuk mensimulasikan data latih.
- "bmi_bias" dan "tensi_bias" HANYA diisi untuk kondisi yang secara umum
  memang berkorelasi dengan berat badan/tekanan darah (mis. Hipertensi,
  Diabetes Tipe 2). Untuk kondisi lain sengaja dibiarkan None (netral) —
  supaya model TIDAK belajar asosiasi palsu yang tidak berdasar.
- Kalau user memilih "tidak tahu"/"tidak mau jawab", nilainya dipetakan ke
  kategori "tidak_tahu" yang SENGAJA disebar merata ke semua penyakit saat
  membuat data latih (lihat generate_training_data.py) — supaya model
  belajar bahwa "tidak tahu" tidak memihak ke kondisi manapun.
"""

BMI_CATEGORIES = ["kurus", "normal", "gemuk", "obesitas", "tidak_tahu"]
TENSI_CATEGORIES = ["normal", "agak_tinggi", "tinggi", "tidak_tahu"]
DURATION_CATEGORIES = ["kurang_3_hari", "3_7_hari", "1_4_minggu", "lebih_1_bulan", "tidak_tahu"]

DURATION_ARCHETYPES = {
    "akut":       {"kurang_3_hari": 0.45, "3_7_hari": 0.35, "1_4_minggu": 0.15, "lebih_1_bulan": 0.05},
    "subakut":    {"kurang_3_hari": 0.15, "3_7_hari": 0.30, "1_4_minggu": 0.35, "lebih_1_bulan": 0.20},
    "kronis":     {"kurang_3_hari": 0.05, "3_7_hari": 0.10, "1_4_minggu": 0.25, "lebih_1_bulan": 0.60},
    "bervariasi": {"kurang_3_hari": 0.25, "3_7_hari": 0.25, "1_4_minggu": 0.25, "lebih_1_bulan": 0.25},
}

BMI_BIAS_HIGH = {"kurus": 0.05, "normal": 0.25, "gemuk": 0.40, "obesitas": 0.30}
BMI_BIAS_NEUTRAL = {"kurus": 0.15, "normal": 0.55, "gemuk": 0.20, "obesitas": 0.10}

TENSI_BIAS_HIGH = {"normal": 0.15, "agak_tinggi": 0.30, "tinggi": 0.55}
TENSI_BIAS_NEUTRAL = {"normal": 0.55, "agak_tinggi": 0.30, "tinggi": 0.15}

SYMPTOM_GROUPS = {
    "Umum": {
        "demam": "Demam (badan hangat/meriang)",
        "demam_tinggi_mendadak": "Demam tinggi yang muncul mendadak",
        "menggigil": "Menggigil",
        "lemas": "Badan lemas",
        "kelelahan": "Kelelahan berkepanjangan",
        "keringat_malam": "Berkeringat berlebihan di malam hari",
        "penurunan_berat_badan": "Penurunan berat badan tanpa sebab jelas",
        "nafsu_makan_menurun": "Nafsu makan menurun",
    },
    "Pernapasan & THT": {
        "batuk_kering": "Batuk kering",
        "batuk_berdahak": "Batuk berdahak",
        "pilek": "Pilek / hidung berair",
        "hidung_tersumbat": "Hidung tersumbat",
        "bersin_bersin": "Sering bersin",
        "sakit_tenggorokan": "Sakit tenggorokan",
        "suara_serak": "Suara serak",
        "sulit_menelan": "Sulit/nyeri saat menelan",
        "sesak_napas": "Sesak napas",
        "mengi": "Napas berbunyi 'ngik' (mengi)",
        "nyeri_dada": "Nyeri dada",
        "telinga_nyeri": "Nyeri telinga",
        "telinga_berdenging": "Telinga berdenging",
        "pendengaran_menurun": "Pendengaran menurun",
        "kelenjar_getah_bening_bengkak": "Kelenjar getah bening bengkak (leher)",
    },
    "Kepala & Saraf": {
        "sakit_kepala": "Sakit kepala",
        "sakit_kepala_sebelah": "Sakit kepala sebelah / berdenyut",
        "nyeri_belakang_mata": "Nyeri di belakang mata",
        "pusing_berputar": "Pusing berputar (vertigo)",
        "sulit_konsentrasi": "Sulit berkonsentrasi",
        "sensitif_cahaya": "Sensitif terhadap cahaya",
    },
    "Pencernaan": {
        "mual": "Mual",
        "muntah": "Muntah",
        "diare": "Diare",
        "sembelit": "Sembelit",
        "nyeri_perut": "Nyeri perut (umum)",
        "nyeri_perut_kanan_bawah": "Nyeri perut kanan bawah",
        "nyeri_ulu_hati": "Nyeri ulu hati",
        "kembung": "Perut kembung",
        "sering_bersendawa": "Sering bersendawa",
        "mata_kuning": "Mata/kulit menguning",
        "urin_gelap": "Urin berwarna gelap",
    },
    "Kulit & Mata": {
        "ruam_kulit": "Ruam kulit",
        "gatal_gatal": "Gatal-gatal",
        "kulit_kering": "Kulit kering",
        "lepuhan_kulit_sebelah_tubuh": "Lepuhan kulit di satu sisi tubuh",
        "nyeri_saraf_kulit": "Nyeri seperti terbakar di kulit",
        "mata_merah": "Mata merah",
        "mata_gatal": "Mata gatal",
        "mata_berair": "Mata berair",
    },
    "Otot, Sendi & Kemih": {
        "nyeri_sendi": "Nyeri sendi",
        "bengkak_sendi": "Sendi bengkak",
        "kaku_sendi_pagi": "Sendi kaku di pagi hari",
        "nyeri_otot": "Nyeri otot",
        "nyeri_pinggang": "Nyeri pinggang",
        "sering_buang_air_kecil": "Sering buang air kecil",
        "nyeri_saat_kencing": "Nyeri saat buang air kecil",
        "urin_keruh": "Urin keruh",
    },
    "Jantung & Hormon": {
        "jantung_berdebar": "Jantung berdebar",
        "bengkak_kaki": "Bengkak pada kaki",
        "tangan_gemetar": "Tangan gemetar",
        "intoleransi_panas": "Tidak tahan cuaca panas",
        "intoleransi_dingin": "Tidak tahan cuaca dingin",
    },
    "Kondisi Psikologis": {
        "cemas_berlebihan": "Cemas berlebihan",
        "sulit_tidur": "Sulit tidur",
        "mudah_tersinggung": "Mudah tersinggung/marah",
        "mood_turun_berkepanjangan": "Suasana hati menurun berkepanjangan",
    },
}

ALL_SYMPTOMS = {k: v for group in SYMPTOM_GROUPS.values() for k, v in group.items()}

RED_FLAG_SYMPTOMS = {
    "nyeri_dada",
    "sesak_napas",
    "nyeri_perut_kanan_bawah",
    "demam_tinggi_mendadak",
}

DISEASES = {
    "Influenza (Flu)": {
        "symptoms": {"demam": 0.85, "menggigil": 0.6, "lemas": 0.8, "nyeri_otot": 0.7,
                     "sakit_kepala": 0.6, "batuk_kering": 0.6, "sakit_tenggorokan": 0.5, "pilek": 0.4},
        "specialist": "Dokter Umum", "category": "Infeksi virus umum", "urgent": False,
        "description": "Infeksi virus saluran napas yang menyerang seluruh tubuh, biasanya membaik sendiri dalam beberapa hari.",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
    "Selesma (Common Cold)": {
        "symptoms": {"pilek": 0.9, "hidung_tersumbat": 0.8, "bersin_bersin": 0.7,
                     "sakit_tenggorokan": 0.5, "batuk_kering": 0.4, "demam": 0.2},
        "specialist": "Dokter Umum", "category": "Infeksi virus umum", "urgent": False,
        "description": "Infeksi virus ringan pada hidung dan tenggorokan bagian atas.",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
    "Migrain": {
        "symptoms": {"sakit_kepala_sebelah": 0.9, "nyeri_belakang_mata": 0.5, "mual": 0.6,
                     "sensitif_cahaya": 0.7, "muntah": 0.3},
        "specialist": "Neurologis (Dokter Saraf)", "category": "Gangguan saraf", "urgent": False,
        "description": "Sakit kepala berdenyut yang sering di satu sisi, umumnya disertai mual dan sensitif cahaya.",
        "duration_typical": "bervariasi", "bmi_bias": None, "tensi_bias": None,
    },
    "Sakit Kepala Tegang (Tension Headache)": {
        "symptoms": {"sakit_kepala": 0.85, "lemas": 0.3, "sulit_konsentrasi": 0.3},
        "specialist": "Dokter Umum / Neurologis", "category": "Gangguan saraf", "urgent": False,
        "description": "Sakit kepala akibat ketegangan otot, terasa seperti tekanan di kedua sisi kepala.",
        "duration_typical": "bervariasi", "bmi_bias": None, "tensi_bias": None,
    },
    "Gastritis (Maag)": {
        "symptoms": {"nyeri_ulu_hati": 0.85, "mual": 0.6, "kembung": 0.6,
                     "sering_bersendawa": 0.5, "nafsu_makan_menurun": 0.4},
        "specialist": "Gastroenterologis (Penyakit Dalam)", "category": "Pencernaan", "urgent": False,
        "description": "Peradangan pada dinding lambung.",
        "duration_typical": "subakut", "bmi_bias": None, "tensi_bias": None,
    },
    "GERD (Asam Lambung Naik)": {
        "symptoms": {"nyeri_ulu_hati": 0.7, "sering_bersendawa": 0.6, "sulit_menelan": 0.3,
                     "suara_serak": 0.3, "batuk_kering": 0.3},
        "specialist": "Gastroenterologis (Penyakit Dalam)", "category": "Pencernaan", "urgent": False,
        "description": "Naiknya asam lambung ke kerongkongan yang menyebabkan rasa terbakar.",
        "duration_typical": "kronis", "bmi_bias": "tinggi", "tensi_bias": None,
    },
    "Diare Akut": {
        "symptoms": {"diare": 0.95, "nyeri_perut": 0.6, "mual": 0.5, "lemas": 0.4, "demam": 0.3},
        "specialist": "Dokter Umum / Gastroenterologis", "category": "Pencernaan", "urgent": False,
        "description": "Buang air besar cair lebih sering dari biasanya, sering akibat infeksi.",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
    "Infeksi Saluran Kemih (ISK)": {
        "symptoms": {"nyeri_saat_kencing": 0.85, "sering_buang_air_kecil": 0.8, "urin_keruh": 0.6,
                     "nyeri_pinggang": 0.4, "demam": 0.3},
        "specialist": "Urologis", "category": "Saluran kemih", "urgent": False,
        "description": "Infeksi pada saluran kemih, paling umum terjadi pada kandung kemih.",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
    "Faringitis": {
        "symptoms": {"sakit_tenggorokan": 0.9, "sulit_menelan": 0.6, "demam": 0.4,
                     "kelenjar_getah_bening_bengkak": 0.4},
        "specialist": "THT (Telinga Hidung Tenggorokan)", "category": "THT", "urgent": False,
        "description": "Peradangan pada tenggorokan (faring).",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
    "Sinusitis": {
        "symptoms": {"hidung_tersumbat": 0.8, "sakit_kepala": 0.6, "nyeri_belakang_mata": 0.4,
                     "pilek": 0.5, "demam": 0.3},
        "specialist": "THT", "category": "THT", "urgent": False,
        "description": "Peradangan pada rongga sinus di sekitar hidung.",
        "duration_typical": "subakut", "bmi_bias": None, "tensi_bias": None,
    },
    "Rhinitis Alergi": {
        "symptoms": {"bersin_bersin": 0.85, "hidung_tersumbat": 0.6, "mata_gatal": 0.6,
                     "mata_berair": 0.5, "pilek": 0.5},
        "specialist": "THT / Alergi-Imunologi", "category": "Alergi", "urgent": False,
        "description": "Reaksi alergi pada saluran hidung terhadap pemicu seperti debu atau serbuk sari.",
        "duration_typical": "kronis", "bmi_bias": None, "tensi_bias": None,
    },
    "Asma": {
        "symptoms": {"sesak_napas": 0.85, "mengi": 0.8, "batuk_kering": 0.5, "nyeri_dada": 0.3},
        "specialist": "Pulmonologis (Dokter Paru)", "category": "Pernapasan", "urgent": False,
        "description": "Penyempitan saluran napas yang menyebabkan sesak dan napas berbunyi.",
        "duration_typical": "bervariasi", "bmi_bias": None, "tensi_bias": None,
    },
    "Bronkitis Akut": {
        "symptoms": {"batuk_berdahak": 0.85, "lemas": 0.4, "sesak_napas": 0.4,
                     "nyeri_dada": 0.3, "demam": 0.3},
        "specialist": "Pulmonologis / Dokter Umum", "category": "Pernapasan", "urgent": False,
        "description": "Peradangan pada saluran bronkus di paru-paru.",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
    "Hipertensi": {
        "symptoms": {"sakit_kepala": 0.5, "pusing_berputar": 0.3, "jantung_berdebar": 0.3, "lemas": 0.2},
        "specialist": "Kardiologis / Penyakit Dalam", "category": "Kardiovaskular", "urgent": False,
        "description": "Tekanan darah tinggi yang sering tidak menimbulkan gejala jelas di awal.",
        "duration_typical": "kronis", "bmi_bias": "tinggi", "tensi_bias": "tinggi",
    },
    "Diabetes Melitus Tipe 2": {
        "symptoms": {"sering_buang_air_kecil": 0.6, "lemas": 0.5, "penurunan_berat_badan": 0.4,
                     "kulit_kering": 0.3, "nafsu_makan_menurun": 0.2},
        "specialist": "Endokrinologis / Penyakit Dalam", "category": "Metabolik", "urgent": False,
        "description": "Gangguan metabolisme gula darah kronis.",
        "duration_typical": "kronis", "bmi_bias": "tinggi", "tensi_bias": None,
    },
    "Anemia Defisiensi Besi": {
        "symptoms": {"lemas": 0.85, "kelelahan": 0.7, "pusing_berputar": 0.4,
                     "sesak_napas": 0.3, "jantung_berdebar": 0.3},
        "specialist": "Hematologis / Penyakit Dalam", "category": "Darah", "urgent": False,
        "description": "Kekurangan sel darah merah sehat, sering akibat kurang zat besi.",
        "duration_typical": "kronis", "bmi_bias": None, "tensi_bias": None,
    },
    "Vertigo (Gangguan Keseimbangan)": {
        "symptoms": {"pusing_berputar": 0.9, "mual": 0.5, "muntah": 0.3, "telinga_berdenging": 0.3},
        "specialist": "Neurologis / THT", "category": "Gangguan saraf", "urgent": False,
        "description": "Sensasi berputar yang sering dikaitkan dengan gangguan keseimbangan telinga dalam.",
        "duration_typical": "bervariasi", "bmi_bias": None, "tensi_bias": None,
    },
    "Insomnia": {
        "symptoms": {"sulit_tidur": 0.9, "kelelahan": 0.6, "sulit_konsentrasi": 0.5, "mudah_tersinggung": 0.4},
        "specialist": "Dokter Umum / Psikiater", "category": "Kondisi psikologis", "urgent": False,
        "description": "Kesulitan memulai atau mempertahankan tidur secara berkelanjutan.",
        "duration_typical": "kronis", "bmi_bias": None, "tensi_bias": None,
    },
    "Dermatitis Atopik": {
        "symptoms": {"gatal_gatal": 0.85, "kulit_kering": 0.7, "ruam_kulit": 0.6},
        "specialist": "Dermatologis (Dokter Kulit)", "category": "Kulit", "urgent": False,
        "description": "Peradangan kulit kronis yang menyebabkan rasa gatal dan kulit kering.",
        "duration_typical": "kronis", "bmi_bias": None, "tensi_bias": None,
    },
    "Konjungtivitis": {
        "symptoms": {"mata_merah": 0.9, "mata_gatal": 0.6, "mata_berair": 0.6},
        "specialist": "Oftalmologis (Dokter Mata)", "category": "Mata", "urgent": False,
        "description": "Peradangan pada selaput bening yang melapisi bagian putih mata.",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
    "Otitis Media Akut": {
        "symptoms": {"telinga_nyeri": 0.85, "demam": 0.4, "pendengaran_menurun": 0.4},
        "specialist": "THT", "category": "THT", "urgent": False,
        "description": "Infeksi pada telinga tengah, sering terjadi setelah pilek.",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
    "Tonsilitis": {
        "symptoms": {"sakit_tenggorokan": 0.85, "sulit_menelan": 0.6, "demam": 0.5,
                     "kelenjar_getah_bening_bengkak": 0.5},
        "specialist": "THT", "category": "THT", "urgent": False,
        "description": "Peradangan pada amandel (tonsil).",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
    "Apendisitis Akut (Radang Usus Buntu)": {
        "symptoms": {"nyeri_perut_kanan_bawah": 0.9, "mual": 0.5, "muntah": 0.4,
                     "demam": 0.4, "nafsu_makan_menurun": 0.4},
        "specialist": "Bedah Umum — SEGERA", "category": "Kedaruratan bedah", "urgent": True,
        "description": "Peradangan pada usus buntu yang dapat memburuk cepat dan butuh penanganan segera.",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
    "Batu Ginjal (Nefrolitiasis)": {
        "symptoms": {"nyeri_pinggang": 0.85, "nyeri_saat_kencing": 0.4, "urin_keruh": 0.3, "mual": 0.4},
        "specialist": "Urologis", "category": "Saluran kemih", "urgent": False,
        "description": "Endapan keras mineral yang terbentuk di ginjal atau saluran kemih.",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
    "Demam Berdarah Dengue (DBD)": {
        "symptoms": {"demam_tinggi_mendadak": 0.9, "sakit_kepala": 0.5, "nyeri_otot": 0.6,
                     "ruam_kulit": 0.4, "mual": 0.3, "lemas": 0.5},
        "specialist": "Penyakit Dalam — SEGERA", "category": "Infeksi arbovirus", "urgent": True,
        "description": "Infeksi virus yang ditularkan nyamuk Aedes aegypti, dapat memburuk cepat.",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
    "Demam Tifoid (Tifus)": {
        "symptoms": {"demam": 0.85, "sakit_kepala": 0.5, "lemas": 0.6, "nafsu_makan_menurun": 0.5,
                     "nyeri_perut": 0.4, "sembelit": 0.3},
        "specialist": "Penyakit Dalam", "category": "Infeksi bakteri", "urgent": False,
        "description": "Infeksi bakteri Salmonella typhi, umumnya melalui makanan/air yang terkontaminasi.",
        "duration_typical": "subakut", "bmi_bias": None, "tensi_bias": None,
    },
    "COVID-19": {
        "symptoms": {"demam": 0.6, "batuk_kering": 0.6, "kelelahan": 0.6, "sesak_napas": 0.3,
                     "sakit_tenggorokan": 0.3, "pilek": 0.3},
        "specialist": "Dokter Umum / Penyakit Dalam", "category": "Infeksi virus", "urgent": False,
        "description": "Infeksi virus SARS-CoV-2 yang menyerang saluran pernapasan.",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
    "Chikungunya": {
        "symptoms": {"demam_tinggi_mendadak": 0.8, "nyeri_sendi": 0.85, "bengkak_sendi": 0.5,
                     "ruam_kulit": 0.4, "sakit_kepala": 0.4},
        "specialist": "Penyakit Dalam", "category": "Infeksi arbovirus", "urgent": False,
        "description": "Infeksi virus dari gigitan nyamuk yang khas menyebabkan nyeri sendi hebat.",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
    "Hepatitis A": {
        "symptoms": {"mata_kuning": 0.8, "urin_gelap": 0.7, "lemas": 0.6,
                     "nafsu_makan_menurun": 0.5, "mual": 0.5, "demam": 0.3},
        "specialist": "Gastroenterologis / Penyakit Dalam", "category": "Infeksi hati", "urgent": False,
        "description": "Infeksi virus pada hati, umumnya menular lewat makanan/air yang terkontaminasi.",
        "duration_typical": "subakut", "bmi_bias": None, "tensi_bias": None,
    },
    "Hipotiroidisme": {
        "symptoms": {"kelelahan": 0.7, "intoleransi_dingin": 0.7, "kulit_kering": 0.5,
                     "mudah_tersinggung": 0.3, "sembelit": 0.3},
        "specialist": "Endokrinologis", "category": "Hormon", "urgent": False,
        "description": "Kelenjar tiroid yang kurang aktif sehingga memperlambat metabolisme tubuh.",
        "duration_typical": "kronis", "bmi_bias": "tinggi", "tensi_bias": None,
    },
    "Hipertiroidisme": {
        "symptoms": {"penurunan_berat_badan": 0.6, "jantung_berdebar": 0.6, "tangan_gemetar": 0.6,
                     "intoleransi_panas": 0.6, "mudah_tersinggung": 0.4, "sulit_tidur": 0.3},
        "specialist": "Endokrinologis", "category": "Hormon", "urgent": False,
        "description": "Kelenjar tiroid yang terlalu aktif sehingga mempercepat metabolisme tubuh.",
        "duration_typical": "kronis", "bmi_bias": None, "tensi_bias": None,
    },
    "Sindrom Iritasi Usus (IBS)": {
        "symptoms": {"nyeri_perut": 0.7, "kembung": 0.6, "diare": 0.4, "sembelit": 0.4},
        "specialist": "Gastroenterologis", "category": "Pencernaan", "urgent": False,
        "description": "Gangguan fungsi usus kronis tanpa kerusakan struktural yang jelas.",
        "duration_typical": "kronis", "bmi_bias": None, "tensi_bias": None,
    },
    "Osteoartritis": {
        "symptoms": {"nyeri_sendi": 0.85, "kaku_sendi_pagi": 0.6, "bengkak_sendi": 0.4, "nyeri_otot": 0.3},
        "specialist": "Ortopedis / Reumatologis", "category": "Muskuloskeletal", "urgent": False,
        "description": "Keausan tulang rawan sendi akibat penggunaan jangka panjang, umum pada usia lanjut.",
        "duration_typical": "kronis", "bmi_bias": "tinggi", "tensi_bias": None,
    },
    "Herpes Zoster (Cacar Api)": {
        "symptoms": {"lepuhan_kulit_sebelah_tubuh": 0.9, "nyeri_saraf_kulit": 0.8,
                     "demam": 0.3, "kelelahan": 0.3},
        "specialist": "Dermatologis (Dokter Kulit)", "category": "Kulit", "urgent": False,
        "description": "Reaktivasi virus cacar air yang menyebabkan ruam lepuh nyeri di satu sisi tubuh.",
        "duration_typical": "subakut", "bmi_bias": None, "tensi_bias": None,
    },
    "Gangguan Cemas (Anxiety Disorder)": {
        "symptoms": {"cemas_berlebihan": 0.85, "jantung_berdebar": 0.5, "sulit_tidur": 0.5,
                     "sulit_konsentrasi": 0.4, "mudah_tersinggung": 0.3},
        "specialist": "Psikiater / Psikolog Klinis", "category": "Kondisi psikologis", "urgent": False,
        "description": "Kecemasan berlebihan yang menetap dan mengganggu aktivitas sehari-hari.",
        "duration_typical": "kronis", "bmi_bias": None, "tensi_bias": None,
    },
    "Malaria": {
        "symptoms": {"demam_tinggi_mendadak": 0.8, "menggigil": 0.8, "sakit_kepala": 0.5,
                     "nyeri_otot": 0.5, "keringat_malam": 0.4, "mual": 0.3},
        "specialist": "Penyakit Dalam — SEGERA", "category": "Infeksi parasit", "urgent": True,
        "description": "Infeksi parasit yang ditularkan nyamuk Anopheles, umum di daerah endemis.",
        "duration_typical": "akut", "bmi_bias": None, "tensi_bias": None,
    },
}

DISEASE_LIST = list(DISEASES.keys())


def bmi_from_bb_tb(bb_kg, tb_cm):
    """Hitung kategori BMI dari berat (kg) dan tinggi (cm). Return None kalau
    salah satu input tidak ada — dipetakan ke kategori 'tidak_tahu' di API."""
    if not bb_kg or not tb_cm or tb_cm <= 0:
        return None
    bmi = bb_kg / ((tb_cm / 100) ** 2)
    if bmi < 18.5:
        return "kurus"
    if bmi < 25:
        return "normal"
    if bmi < 30:
        return "gemuk"
    return "obesitas"
