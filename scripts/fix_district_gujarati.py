import psycopg2

GUJARAT_DISTRICTS = [
    ("Gir Somnath", "ગીર સોમનાથ", 474),
    ("Porbandar", "પોરબંદર", 479),
    ("Navsari", "નવસારી", 492),
    ("Valsad", "વલસાડ", 499),
    ("Junagadh", "જૂનાગઢ", 478),
    ("Devbhumi Dwarka", "દેવભૂમિ દ્વારકા", 682),
    ("Kutch", "કચ્છ", 468),
    ("Amreli", "અમરેલી", 475),
    ("Bhavnagar", "ભાવનગર", 476),
    ("Jamnagar", "જામનગર", 477),
    ("Morbi", "મોરબી", 683),
    ("Rajkot", "રાજકોટ", 480),
    ("Surendranagar", "સુરેન્દ્રનગર", 481),
    ("Ahmedabad", "અમદાવાદ", 470),
    ("Anand", "આણંદ", 482),
    ("Bharuch", "ભરૂચ", 483),
    ("Surat", "સુરત", 493),
    ("Dang", "ડાંગ", 494),
    ("Tapi", "તાપી", 680),
    ("Narmada", "નર્મદા", 491),
    ("Vadodara", "વડોદરા", 486),
    ("Chhota Udaipur", "છોટા ઉદેપુર", 681),
    ("Panchmahal", "પંચમહાલ", 485),
    ("Mahisagar", "મહીસાગર", 684),
    ("Dahod", "દાહોદ", 487),
    ("Kheda", "ખેડા", 484),
    ("Gandhinagar", "ગાંધીનગર", 471),
    ("Mehsana", "મહેસાણા", 473),
    ("Patan", "પાટણ", 472),
    ("Banaskantha", "બનાસકાંઠા", 469),
    ("Sabarkantha", "સાબરકાંઠા", 488),
    ("Aravalli", "અરવલ્લી", 685),
    ("Botad", "બોટાદ", 686),
]

def update_districts():
    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/sardrishti")
    conn.set_client_encoding('UTF8')
    cur = conn.cursor()
    for name, name_gu, lgd in GUJARAT_DISTRICTS:
        cur.execute(
            """
            UPDATE districts 
            SET name_gu = %s, lgd_code = %s 
            WHERE name ILIKE %s OR name ILIKE %s
            """,
            (name_gu, lgd, f"%{name}%", f"%{name.replace(' ', '')}%")
        )
    conn.commit()
    cur.execute("SELECT id, name, name_gu FROM districts ORDER BY id LIMIT 5")
    print("Updated sample:", cur.fetchall())
    conn.close()

if __name__ == "__main__":
    update_districts()

