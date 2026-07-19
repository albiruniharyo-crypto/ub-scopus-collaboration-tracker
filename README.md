# UB Scopus Collaboration Tracker

Aplikasi lokal untuk menemukan dan memantau calon kolaborator internasional pada patologi anatomi veteriner, onkologi komparatif, penyakit infeksi, serta digital pathology.

## Keamanan penting

API key yang pernah dikirim melalui percakapan sebaiknya segera **di-rotate**. Paket ini tidak menyimpan API key tersebut. Gunakan key baru melalui file `.env`; jangan commit `.env` ke Git.

## Fitur

- Mengambil dokumen dari Scopus Search API.
- Mengumpulkan Scopus Author ID dari publikasi relevan.
- Mengambil Author Profile dan H-index melalui Author Retrieval API.
- Menyimpan kandidat ke SQLite.
- Menyaring H-index minimum 35.
- Dashboard Streamlit, ekspor CSV, filter negara dan kata kunci.
- Empat query awal: patologi anatomi veteriner, comparative oncology, digital pathology/AI, dan infectious disease pathology.

## Instalasi

```bash
python -m venv .venv
```

Aktifkan environment:

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Instal:
```bash
pip install -r requirements.txt
```

Salin konfigurasi:
```bash
cp .env.example .env
```

Pada Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

Isi `.env` dengan API key baru.

## Menjalankan pengambilan data

```bash
python pipeline.py --query-name veterinary_anatomic_pathology --max-documents 150 --h-index-min 35
python pipeline.py --query-name comparative_oncology --max-documents 150 --h-index-min 35
python pipeline.py --query-name digital_pathology_ai --max-documents 150 --h-index-min 35
python pipeline.py --query-name infectious_disease_pathology --max-documents 150 --h-index-min 35
```

## Menjalankan dashboard

```bash
streamlit run app.py
```

Kemudian buka alamat lokal yang ditampilkan Streamlit.

## Catatan akses

API key saja belum tentu memberikan seluruh entitlement. Full API access mengikuti afiliasi dan langganan institusi. Jalankan dari jaringan kampus/VPN UB bila diperlukan. Jika UB memperoleh Institutional Token dari Elsevier, isikan pada `ELSEVIER_INST_TOKEN`.

## Pengembangan berikutnya

- Tambahkan pemeringkatan QS institusi.
- Tambahkan email institusional dari sumber resmi.
- Tambahkan analisis co-author network.
- Tambahkan scoring kecocokan per tema prioritas rektor.
- Integrasikan hasil terpilih ke Google Calendar dan Gmail setelah peninjauan manusia.
