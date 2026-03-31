from datetime import datetime
import urllib.parse

def convert_date(date_str):
    # formato da data original
    fmt = "%a, %B %d, %Y at %I:%M:%S %p"
    
    dt = datetime.strptime(date_str, fmt)
    
    # formata para ISO
    iso = dt.strftime("%Y-%m-%dT%H:%M:%S-03:00")
    
    # encode para URL (%3A)
    encoded = iso.replace(":", "%3A")
    
    return encoded


inicio = "Tue, March 24, 2026 at 8:55:27 PM"
fim = "Tue, March 24, 2026 at 9:04:22 PM"

print("Inicial:", convert_date(inicio))
print("Final:", convert_date(fim))