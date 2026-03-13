"""Lookup table of common Indonesian acronyms and abbreviations.

Used by the preprocessor to expand acronyms before LightRAG ingestion,
improving entity extraction quality for Indonesian-language text.

This table is intentionally curated for the **news / fact-checking** domain
(government institutions, agencies, media outlets, legal terms).
"""

from __future__ import annotations

INDONESIAN_ACRONYMS: dict[str, str] = {
    # --- Government institutions ---
    "BPJS": "Badan Penyelenggara Jaminan Sosial",
    "BPOM": "Badan Pengawas Obat dan Makanan",
    "BNPB": "Badan Nasional Penanggulangan Bencana",
    "BNPT": "Badan Nasional Penanggulangan Terorisme",
    "BPBD": "Badan Penanggulangan Bencana Daerah",
    "BIN": "Badan Intelijen Negara",
    "BPS": "Badan Pusat Statistik",
    "BKKBN": "Badan Kependudukan dan Keluarga Berencana Nasional",
    "BMKG": "Badan Meteorologi, Klimatologi, dan Geofisika",
    "BRIN": "Badan Riset dan Inovasi Nasional",
    "BAKAMLA": "Badan Keamanan Laut",
    "BASARNAS": "Badan Nasional Pencarian dan Pertolongan",

    # --- Ministries ---
    "Kemenkes": "Kementerian Kesehatan",
    "Kemendikbud": "Kementerian Pendidikan dan Kebudayaan",
    "Kemendikbudristek": "Kementerian Pendidikan, Kebudayaan, Riset, dan Teknologi",
    "Kemenag": "Kementerian Agama",
    "Kemenkeu": "Kementerian Keuangan",
    "Kemendagri": "Kementerian Dalam Negeri",
    "Kemenlu": "Kementerian Luar Negeri",
    "Kemenhan": "Kementerian Pertahanan",
    "Kemenhub": "Kementerian Perhubungan",
    "Kemensos": "Kementerian Sosial",
    "Kemenkominfo": "Kementerian Komunikasi dan Informatika",
    "Kemenperin": "Kementerian Perindustrian",
    "Kemendag": "Kementerian Perdagangan",
    "Kementan": "Kementerian Pertanian",
    "KemenPUPR": "Kementerian Pekerjaan Umum dan Perumahan Rakyat",
    "KemenESDM": "Kementerian Energi dan Sumber Daya Mineral",
    "Kemenpan-RB": "Kementerian Pendayagunaan Aparatur Negara dan Reformasi Birokrasi",
    "Kemenko PMK": "Kementerian Koordinator Bidang Pembangunan Manusia dan Kebudayaan",
    "Kemenko Polhukam": "Kementerian Koordinator Bidang Politik, Hukum, dan Keamanan",
    "Kemenko Perekonomian": "Kementerian Koordinator Bidang Perekonomian",
    "Kemenko Marves": "Kementerian Koordinator Bidang Kemaritiman dan Investasi",

    # --- Law enforcement & judicial ---
    "KPK": "Komisi Pemberantasan Korupsi",
    "KPU": "Komisi Pemilihan Umum",
    "Bawaslu": "Badan Pengawas Pemilihan Umum",
    "MK": "Mahkamah Konstitusi",
    "MA": "Mahkamah Agung",
    "Polri": "Kepolisian Negara Republik Indonesia",
    "TNI": "Tentara Nasional Indonesia",
    "Kejagung": "Kejaksaan Agung",
    "KY": "Komisi Yudisial",
    "Komnas HAM": "Komisi Nasional Hak Asasi Manusia",
    "OJK": "Otoritas Jasa Keuangan",
    "BI": "Bank Indonesia",

    # --- Legislative ---
    "DPR": "Dewan Perwakilan Rakyat",
    "DPD": "Dewan Perwakilan Daerah",
    "DPRD": "Dewan Perwakilan Rakyat Daerah",
    "MPR": "Majelis Permusyawaratan Rakyat",

    # --- Regulations / legal terms ---
    "UU": "Undang-Undang",
    "PP": "Peraturan Pemerintah",
    "Perpres": "Peraturan Presiden",
    "Perda": "Peraturan Daerah",
    "Inpres": "Instruksi Presiden",
    "Keppres": "Keputusan Presiden",
    "Permen": "Peraturan Menteri",
    "SE": "Surat Edaran",
    "APBN": "Anggaran Pendapatan dan Belanja Negara",
    "APBD": "Anggaran Pendapatan dan Belanja Daerah",

    # --- Health / pandemic ---
    "WHO": "World Health Organization",
    "COVID-19": "Coronavirus Disease 2019",
    "PPKM": "Pemberlakuan Pembatasan Kegiatan Masyarakat",
    "PSBB": "Pembatasan Sosial Berskala Besar",
    "PCR": "Polymerase Chain Reaction",
    "IDAI": "Ikatan Dokter Anak Indonesia",
    "IDI": "Ikatan Dokter Indonesia",
    "BUMN": "Badan Usaha Milik Negara",
    "BUMD": "Badan Usaha Milik Daerah",

    # --- Media / fact-checking ---
    "MAFINDO": "Masyarakat Anti Fitnah Indonesia",
    "AJI": "Aliansi Jurnalis Independen",
    "PWI": "Persatuan Wartawan Indonesia",
    "KPI": "Komisi Penyiaran Indonesia",

    # --- Education ---
    "ITB": "Institut Teknologi Bandung",
    "UI": "Universitas Indonesia",
    "UGM": "Universitas Gadjah Mada",
    "ITS": "Institut Teknologi Sepuluh Nopember",
    "IPB": "Institut Pertanian Bogor",
    "UNPAD": "Universitas Padjadjaran",
    "UNDIP": "Universitas Diponegoro",

    # --- Common abbreviations ---
    "RT": "Rukun Tetangga",
    "RW": "Rukun Warga",
    "KTP": "Kartu Tanda Penduduk",
    "NIK": "Nomor Induk Kependudukan",
    "NKRI": "Negara Kesatuan Republik Indonesia",
    "PKI": "Partai Komunis Indonesia",
    "Ormas": "Organisasi Masyarakat",
    "LSM": "Lembaga Swadaya Masyarakat",
    "NGO": "Non-Governmental Organization",
    "HAM": "Hak Asasi Manusia",
    "PKH": "Program Keluarga Harapan",
    "BLT": "Bantuan Langsung Tunai",
    "BST": "Bantuan Sosial Tunai",
    "Bansos": "Bantuan Sosial",
}
