from jarbas_hive_mind.database import ClientDatabase

name = "JarbasCliTerminal"
access_key = "erpDerPerrDurHUr"
mail = "remote_cli@hivemind.com"


with ClientDatabase() as db:
    db.add_client(name, mail, access_key)
