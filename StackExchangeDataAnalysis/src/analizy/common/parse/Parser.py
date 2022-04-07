import xml.etree.ElementTree as ET
import pandas as pd

#schemat plików z forum jest taki sam, więc nie ma po co wielokrotnie tego pisać

def getData(url):
    tree = ET.parse(url)
    root = tree.getroot()
    return pd.DataFrame([e.attrib for e in root])
