from flask import Flask, jsonify, request
import pymysql

app = Flask(__name__)

def db():
    return pymysql.connect(host="10.3.1.4", user="appuser",
        password="CHANGE_ME", database="miniprojet",
        cursorclass=pymysql.cursors.DictCursor, autocommit=True)

def clean(rows):
    for r in rows:
        r["prix"] = float(r["prix"])
    return rows

@app.get("/api/instruments")
def lister():
    with db() as c, c.cursor() as cur:
        cur.execute("SELECT * FROM instruments ORDER BY id")
        return jsonify(clean(cur.fetchall()))

@app.get("/api/instruments/<int:i>")
def lire(i):
    with db() as c, c.cursor() as cur:
        cur.execute("SELECT * FROM instruments WHERE id=%s", (i,))
        r = cur.fetchone()
    if not r:
        return jsonify(error="introuvable"), 404
    return jsonify(clean([r])[0])

@app.post("/api/instruments")
def creer():
    d = request.get_json()
    with db() as c, c.cursor() as cur:
        cur.execute("INSERT INTO instruments (nom,description,prix,categorie) VALUES (%s,%s,%s,%s)",
            (d["nom"], d.get("description",""), d["prix"], d.get("categorie","")))
        return jsonify(id=cur.lastrowid), 201

@app.put("/api/instruments/<int:i>")
def modifier(i):
    d = request.get_json()
    with db() as c, c.cursor() as cur:
        cur.execute("UPDATE instruments SET nom=%s,description=%s,prix=%s,categorie=%s WHERE id=%s",
            (d["nom"], d.get("description",""), d["prix"], d.get("categorie",""), i))
    return jsonify(ok=True)

@app.delete("/api/instruments/<int:i>")
def supprimer(i):
    with db() as c, c.cursor() as cur:
        cur.execute("DELETE FROM instruments WHERE id=%s", (i,))
    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
