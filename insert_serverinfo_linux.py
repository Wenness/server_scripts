# Script geschreven door Codey Jansen en Wensley de Leeuw

# time voor het aanroepen van de uptime
import time
# shutil voor het aanroepen van opslag informatie
import shutil
# MySQL als database module
import pymysql
# psutil voor het aanroepen van CPU en geheugen informatie
import psutil
# xml.etree.cElementTree voor het aanroepen van het XML configuratie betand
import xml.etree.cElementTree as etree
# datetime date voor het aanroepren van de datum
from datetime import date


def read_config(config): # Voor het aanroepen config bestand

    # Let op: Plaats het XML bestand in dezelfde folder als dit script
    # Locatie XML bestand
    file_location = './config_insert.xml'

    # Probeer het bestand te vinden
    try:
        tree = etree.parse(file_location)
        root = tree.getroot()
        return root.find(config).text
    # Geef anders een fout
    except FileNotFoundError:
        print("!!! Kan XML bestand niet vinden !!!")

def create_connection(): # Aanmaken van de database connectie

    # Lees connectie variabelen uit
    db_host = read_config('db_host')
    db_user = read_config('db_user')
    db_password = read_config('db_password')
    db_name = read_config('db_name')

    # Te beginnen met een lege variabele conn
    connectie = None # Later in script conn
    # Probeer eerst een connectie op te zetten en zet deze in de variabele
    try:
        connectie = pymysql.connect(db_host, db_user, db_password, db_name, autocommit=True)
        return connectie
    except Exception as e:
        print(e)

    return connectie

def fetch_tables(): # Voor het checken van alle tabellen in de database
    
    # Variabele voor database connectie
    conn = create_connection() # Later in script cur
    # Cursor voor SQL
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables;") # Het SQL commando gaat alle tabellen na
    
    return(cursor.fetchall()) # De cursor 'fetched' alle tabel namen

def create_table(conn, create_table_sql): # Voor het aanmaken van een nieuwe tabel in de database
    
    # Probeer een tabel te maken
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Exception as e:
        print(e)

def fill_serverinfo(conn, table_name): # Voor het invullen van de tabel

    # Vind de servernaam locatie in het config bestand
    servernaam = read_config('servernaam')
    # SQL commando met alle tabel waarden
    sql = ''' INSERT INTO ''' + str(servernaam) + ''' (date_today,time,storage_total,storage_used,storage_free,cpu_usage_percentage,mem_usage_percentage,uptime_day,uptime_hour,uptime_minute,uptime_second)
              VALUES('{}','{}',{},{},{},{},{},{},{},{},{}); '''.format(str(table_name[0]), str(table_name[1]), table_name[2], table_name[3], table_name[4], table_name[5], table_name[6], table_name[7], table_name[8], table_name[9], table_name[10])
    
    cur = conn.cursor()
    cur.execute(sql)

def sys_info(): # Voor het aanroepen van CPU usage, geheugen usage en uptime

    # Variabele voor CPU en geheugen gebruik (%)
    cpu_percent = psutil.cpu_percent(interval=1)
    mem_percent = psutil.virtual_memory().percent

    # Variabele voor de uptime
    second = int(time.time()) - int(psutil.boot_time())
    m, s = divmod(second, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    # Variabelen uptime worden in een lijst gezet
    uptime =  [d, h, m, s]

    # Alle variabele in een lijst
    return [cpu_percent, mem_percent, uptime] 

def create_new_server_table(): # Voor het aanmaken van de daadwerkelijke tabel
    
    conn = create_connection()
    servernaam = read_config('servernaam')

    sql_create_server_table = '''CREATE TABLE IF NOT EXISTS `{}`
                                    (`date_today` TEXT,
	                                `time` TEXT NOT NULL,
	                                `storage_total` INTEGER NOT NULL,
	                                `storage_used` INTEGER,
	                                `storage_free` INTEGER,
	                                `cpu_usage_percentage` INTEGER NOT NULL,
	                                `mem_usage_percentage` INTEGER NOT NULL,
	                                `uptime_day` INTEGER,
	                                `uptime_hour` INTEGER,
	                                `uptime_minute` INTEGER,
	                                `uptime_second` INTEGER NOT NULL
                                    );'''.format(servernaam)

    with conn:                  
        create_table(conn, sql_create_server_table)

def insert_serverinfo(): # Voor het invullen van de tabel

    # Hier wordt de totale opslag, gebruikte opslag en vrije opslag in variabelen gezet (GB)
    total, used, free = shutil.disk_usage("/")

    storage_total = str(total // (2**30))
    storage_used = str(used // (2**30))
    storage_free = str(free // (2**30))

    # Variabale voor de datum (jjjj, mm, dd)
    date_today = str(date.today())

    # Variabale voor de tijd (u:m:s)
    t = time.localtime()
    time_now = str(time.strftime("%H:%M:%S", t))

    # Variabele voor de CPU gebruik, geheugen gebruik en uptime
    cpu_mem_uptime  = sys_info() # Zie dit als [CPU gebruik, geheugen gebruik, [uptime dagen, uptime uren, uptime minuten, uptime seconden]]

    # Hieronder wordt de lijst die in variabele 'sys_info' staat opgebroken in aparte variabelen voor het verwerken naar de tabel
    cpu_usage_percentage = cpu_mem_uptime[0]
    mem_usage_percentage = cpu_mem_uptime[1]
    # De lijst in de lijst wordt in een aparte variabele gezet
    uptime = cpu_mem_uptime[2]
    # De lijst van uptime wordt opgebroken voor het verwerken naar de tabel
    uptime_day = uptime[0]
    uptime_hour = uptime[1]
    uptime_minute = uptime[2]
    uptime_second = uptime[3]

    table_name = read_config('servernaam')
    conn = create_connection()
    with conn:
        # Met de connectie vullen we de tabel aan
        table_name = (date_today,time_now,storage_total,storage_used,storage_free,cpu_usage_percentage,mem_usage_percentage,uptime_day,uptime_hour,uptime_minute,uptime_second)
        fill_serverinfo(conn, table_name)

# Als de servernaam niet in de lijst met tabellen staat: Maak een tabel met de servernaam en vul deze aan
if read_config('servernaam') not in str(fetch_tables()):
    create_new_server_table()
    insert_serverinfo()
# Anders vul alleen de bestaande tabel aan
else:
    insert_serverinfo()
