#! /usr/bin/python3

# Script geschreven door Codey Jansen en Wensley de Leeuw

# CGI voor de web functionaliteit
import cgi
# xml.etree.cElementTree voor het aanroepen van het XML configuratie betand
import xml.etree.cElementTree as etree
# MySQL als database module
import pymysql

def read_config(config): # Functie voor het aanroepen config bestand

    # locatie XML bestand
    file_location = './config_management.xml'

    # Probeer het bestand te vinden
    try:
        tree = etree.parse(file_location)
        root = tree.getroot()
        return root.find(config).text
    # Geef anders een fout
    except FileNotFoundError:
        print("!!! Kan XML bestand niet vinden !!!")

# Variabele voor opslag invulveld
form = cgi.FieldStorage()

# Vul de variabele met ingevulde info
servername = form.getvalue('servername')

def create_connection(): # Functie voor het aanmaken van de database connectie

    # Lees connectie variabelen uit
    db_host = read_config('db_host')
    db_user = read_config('db_user')
    db_password = read_config('db_password')
    db_name = read_config('db_name')

    # Te beginnen met een lege variabele conn
    connectie = None # Later in script conn
    # Probeer eerst een connectie op te zetten en zet deze in de variabele
    try:
        connectie = pymysql.connect(db_host, db_user, db_password, db_name)
        return connectie
    except Exception as e:
        print(e)
 
    return connectie

def select_all_serverinfo(conn): # Voor het ophalen tabel inhoud
    
    cursor = conn.cursor() # Later in script cur
    cursor.execute("SELECT * FROM " + str(servername))

    # Voeg tabel inhoud in lijst
    rows = cursor.fetchall()
    table_contents = []
    for row in rows:
        table_contents.append(row)

    return table_contents

conn = create_connection()

# Alle info van tabel
all_info = (select_all_serverinfo(conn))

# Begin HTML
print ("Content-type:text/html\n\n")
print ('<html><head><link rel="stylesheet" type="text/css" href="site.css"></head><body>')
print ("<h2>" + str(servername) + " info: </h2>")
# Met conn maak tabel en vul tabel
with conn:
        print('<table class="blueTable">')
        print("<thead>")
        print("<tr>")
        print("<th>Datum</th>")
        print("<th>Tijd</th>")
        print("<th>Totale opslag</th>")
        print("<th>Gerbuikte opslag</th>")
        print("<th>Vrije opslag</th>")
        print("<th>CPU gebruik</th>")
        print("<th>Geheugen gebruik</th>")
        print("<th>Uptime dagen</th>")
        print("<th>Uptime uren</th>")
        print("<th>Uptime minuten</th>")
        print("<th>Uptime seconden</th>")
        print("</tr>")
        print("<thead>")

        print("<tbody>")
        for item in all_info:
                print("<tr><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th></tr>".format(item[0],item[1],str(item[2]) + " GB",str(item[3]) + " GB",str(item[4]) + " GB",str(item[5]) + "%",str(item[6]) + "%",item[7],item[8],item[9],item[10]))
        print("</tbody>")
        print("</table>")
# Eind HTML
print ("</body></html>")
