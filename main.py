import sqlite3
import random
import string
import time
import datetime

# ======================
# CONNECT DB
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
    SELECT id, username FROM users
    WHERE no_hp=? AND password=?
    """, (no_hp, password))

    user = cursor.fetchone()

    if user:
        print("\n=== LOGIN BERHASIL ===")
        print("Selamat datang", user[1])
        break
    else:
        print("Login gagal")

# ======================
# MENU
# ======================
while True:

    print("\n=== MENU ===")
    print("1. Pesan Tiket")
    print("2. Lihat Tiket")
    print("3. Cancel Tiket")
    print("4. Top Up Wallet")
    print("5. Cek Saldo")
    print("6. Cek Transaksi")
    print("7. Logout")

    menu = input("Pilih: ")

    # ======================
    # PESAN TIKET (PAKAI SALDO WALLET)
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
                print(no, ".", k[1], "| Rp", k[4])
                hasil.append(k)
                no += 1

        if not hasil:
            print("Tidak ada kereta")
            continue

        pilih = int(input("Pilih kereta: "))
        tiket = hasil[pilih - 1]

        seat = input("Pilih seat: ").upper()

        cursor.execute("""
        SELECT status FROM seats
        WHERE kereta_id=? AND seat=?
        """, (tiket[0], seat))

        cek = cursor.fetchone()

        if not cek or cek[0] == "booked":
            print("Seat tidak tersedia")
            continue

        # CEK SALDO
        cursor.execute("SELECT saldo FROM users WHERE id=?", (user[0],))
        saldo = cursor.fetchone()[0]

        if saldo < tiket[4]:
            print("Saldo tidak cukup")
            continue

        # POTONG SALDO
        cursor.execute("""
        UPDATE users
        SET saldo = saldo - ?
        WHERE id=?
        """, (tiket[4], user[0]))

        # BOOK SEAT
        cursor.execute("""
        UPDATE seats
        SET status='booked'
        WHERE kereta_id=? AND seat=?
        """, (tiket[0], seat))

        kode = "TK-" + ''.join(random.choices(string.digits, k=5))

        cursor.execute("""
        INSERT INTO bookings (
            user_id, kereta_id, kereta, asal, tujuan, seat, harga, kode_booking, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
        """, (
            user[0],
            tiket[0],
            tiket[1],
            tiket[2],
            tiket[3],
            seat,
            tiket[4],
            kode
        ))

        db.commit()

        print("\nTiket berhasil dibeli:", kode)

    # ======================
    # LIHAT TIKET
    # ======================
    elif menu == "2":
        cursor.execute("""
        SELECT kereta, asal, tujuan, seat, kode_booking
        FROM bookings
        WHERE user_id=? AND status='ACTIVE'
        """, (user[0],))

        data = cursor.fetchall()

        print("\n=== TIKET SAYA ===")
        if not data:
            print("Belum ada tiket")
        else:
            for d in data:
                print(d)

    # ======================
    # CANCEL + REFUND
    # ======================
    elif menu == "3":
        kode = input("Masukkan kode booking: ").upper()

        cursor.execute("""
        SELECT kereta_id, seat, harga FROM bookings
        WHERE kode_booking=? AND user_id=? AND status='ACTIVE'
        """, (kode, user[0]))

        data = cursor.fetchone()

        if not data:
            print("Tiket tidak ditemukan")
            continue

        kereta_id, seat, harga = data

        cursor.execute("""
        UPDATE bookings
        SET status='CANCELED'
        WHERE kode_booking=?
        """, (kode,))

        cursor.execute("""
        UPDATE seats
        SET status='available'
        WHERE kereta_id=? AND seat=?
        """, (kereta_id, seat))

        cursor.execute("""
        UPDATE users
        SET saldo = saldo + ?
        WHERE id=?
        """, (harga, user[0]))

        db.commit()

        print("Cancel berhasil + refund masuk wallet")

    # ======================
    # TOP UP WALLET (PENDING SYSTEM)
    # ======================
    elif menu == "4":

        nominal = int(input("Nominal top up: "))

        print("\n1. QRIS")
        print("2. VA")
        method = input("Pilih metode: ")

        kode = "TOP-" + ''.join(random.choices(string.digits, k=6))
        waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO transactions (
            user_id, kode_transaksi, type, amount, method, status, created_at
        ) VALUES (?, ?, 'TOPUP', ?, ?, 'PENDING', ?)
        """, (user[0], kode, nominal, method, waktu))

        db.commit()

        print("\nKode transaksi:", kode)
        print("Status: PENDING")

        # simulasi payment otomatis
        status = random.choice(["PAID", "FAILED"])

        cursor.execute("""
        UPDATE transactions
        SET status=?
        WHERE kode_transaksi=?
        """, (status, kode))

        if status == "PAID":
            cursor.execute("""
            UPDATE users
            SET saldo = saldo + ?
            WHERE id=?
            """, (nominal, user[0]))

        db.commit()

        print("Payment result:", status)

    # ======================
    # CEK SALDO
    # ======================
    elif menu == "5":
        cursor.execute("SELECT saldo FROM users WHERE id=?", (user[0],))
        saldo = cursor.fetchone()[0]
        print("Saldo:", saldo)

    # ======================
    # CEK TRANSAKSI
    # ======================
    elif menu == "6":
        cursor.execute("""
        SELECT kode_transaksi, type, amount, status
        FROM transactions
        WHERE user_id=?
        """, (user[0],))

        data = cursor.fetchall()

        print("\n=== TRANSAKSI ===")
        for d in data:
            print(d)

    # ======================
    # LOGOUT
    # ======================
    elif menu == "7":
        print("Logout...")
        break

    else:
        print("Menu salah")
