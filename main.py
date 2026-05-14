import sqlite3
import random
import string
import time

# ======================
# DATABASE
# ======================
db = sqlite3.connect("kereta.db")
cursor = db.cursor()

# ======================
# LOGIN
# ======================
while True:
    no_hp = input("\nMasukkan no HP: ")
    password = input("Masukkan password: ")

    cursor.execute("""
    SELECT * FROM users
    WHERE no_hp=? AND password=?
    """, (no_hp, password))

    user = cursor.fetchone()

    if user:
        print("\n=== LOGIN BERHASIL ===")
        print("Selamat datang", user[1])
        break
    else:
        print("Login gagal, coba lagi")

# ======================
# SEAT MAP
# ======================
def show_seats(kereta_id):

    cursor.execute("""
    SELECT seat, status FROM seats
    WHERE kereta_id=?
    ORDER BY seat
    """, (kereta_id,))

    data = cursor.fetchall()

    print("\n=== SEAT MAP ===")

    for i, s in enumerate(data):

        if s[1] == "booked":
            print("🟥", s[0], end="  ")
        else:
            print("🟩", s[0], end="  ")

        if (i + 1) % 5 == 0:
            print()

# ======================
# E-TICKET
# ======================
def show_eticket(kode, kereta, asal, tujuan, kursi, harga):

    print("\n" + "="*35)
    print("        E - TICKET KERETA")
    print("="*35)
    print("Kode Booking :", kode)
    print("Kereta       :", kereta)
    print("Rute         :", asal, "->", tujuan)
    print("Kursi        :", kursi)
    print("Harga        :", harga)
    print("-"*35)
    print("Status       : PAID / CONFIRMED")
    print("QR Code      : [■■■■■■■■■■] (SIMULASI)")
    print("="*35)

# ======================
# MENU
# ======================
while True:

    print("\n=== MENU ===")
    print("1. Cari & Pesan Tiket")
    print("2. Lihat Tiket Saya")
    print("3. Logout")

    menu = input("Pilih: ")

    # ======================
    # PESAN TIKET
    # ======================
    if menu == "1":

        asal = input("Asal: ").lower()
        tujuan = input("Tujuan: ").lower()

        cursor.execute("SELECT * FROM kereta")
        data = cursor.fetchall()

        hasil = []

        print("\n=== HASIL ===")

        no = 1
        for k in data:
            if k[2].lower() == asal and k[3].lower() == tujuan:
                print(no, ".", k[1], "|", k[2], "->", k[3], "| Rp", k[4])
                hasil.append(k)
                no += 1

        if len(hasil) == 0:
            print("Tidak ada kereta")
            continue

        pilih = int(input("\nPilih kereta: "))
        tiket = hasil[pilih - 1]

        # ======================
        # SEAT MAP
        # ======================
        show_seats(tiket[0])

        seat = input("\nPilih kursi (A1): ").upper()

        cursor.execute("""
        SELECT status FROM seats
        WHERE kereta_id=? AND seat=?
        """, (tiket[0], seat))

        cek = cursor.fetchone()

        if not cek:
            print("Kursi tidak ditemukan")
            continue

        if cek[0] == "booked":
            print("Kursi sudah terisi")
            continue

        # LOCK SEAT
        cursor.execute("""
        UPDATE seats
        SET status='booked'
        WHERE kereta_id=? AND seat=?
        """, (tiket[0], seat))

        db.commit()

        print("\nKursi dipilih:", seat)

        # ======================
        # PAYMENT
        # ======================
        print("\n=== PEMBAYARAN ===")
        print("1. QRIS")
        print("2. Virtual Account")

        metode = input("Pilih metode: ")

        kode_bayar = "PAY-" + str(random.randint(10000, 99999))

        print("\nKode Bayar:", kode_bayar)
        print("Total:", tiket[4])

        if metode == "1":
            print("QRIS (simulasi): SCAN QR")
        elif metode == "2":
            va = "VA" + str(random.randint(1000000000, 9999999999))
            print("VA:", va)
        else:
            print("Metode salah")
            continue

        print("\nMenunggu pembayaran...")
        time.sleep(2)

        status = random.choice(["PAID", "FAILED"])

        print("STATUS:", status)

        if status != "PAID":
            print("Pembayaran gagal")
            continue

        # ======================
        # KODE BOOKING
        # ======================
        kode = "TK-" + ''.join(random.choices(string.digits, k=5))

        # ======================
        # SIMPAN BOOKING
        # ======================
        cursor.execute("""
        INSERT INTO bookings (
            user_id, kereta, asal, tujuan, harga, kode_booking
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user[0],
            tiket[1],
            tiket[2],
            tiket[3],
            tiket[4],
            kode
        ))

        db.commit()

        # ======================
        # E-TICKET TAMPIL
        # ======================
        show_eticket(
            kode,
            tiket[1],
            tiket[2],
            tiket[3],
            seat,
            tiket[4]
        )

    # ======================
    # LIHAT TIKET
    # ======================
    elif menu == "2":

        cursor.execute("""
        SELECT kereta, asal, tujuan, harga, kode_booking
        FROM bookings
        WHERE user_id=?
        """, (user[0],))

        data = cursor.fetchall()

        print("\n=== TIKET SAYA ===")

        if len(data) == 0:
            print("Belum ada tiket")
        else:
            for i, b in enumerate(data):
                print(i+1, ".", b[0], "|", b[1], "->", b[2], "| Rp", b[3], "|", b[4])

    # ======================
    # LOGOUT
    # ======================
    elif menu == "3":
        print("Logout...")
        break

    else:
        print("Menu tidak valid")