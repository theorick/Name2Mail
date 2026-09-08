import time
import re
from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
import pyfiglet

# Fichier dans lequel sauvegarder les adresses valides
FICHIER_RESULTATS = "emails_valides.txt"

def verifier_existence_email(email: str):
    email = email.strip()
    if "@" not in email:
        print("❌ Adresse invalide (format incorrect).")
        return

    domaine = email.split("@")[-1]

    try:
        # 1. Récupération rapide du MX principal avec un timeout de 3 secondes
        resolver = dns.resolver.Resolver()
        resolver.lifetime = 3.0
        reponses = resolver.resolve(domaine, 'MX')
        mx_principal = str(sorted(reponses, key=lambda r: r.preference)[0].exchange).rstrip('.')

        print(f"Connexion à {mx_principal}...")

        # 2. Connexion SMTP rapide (timeout 3s)
        server = smtplib.SMTP(timeout=3)
        server.connect(mx_principal, 25)
        server.helo(domaine)  # Identification propre
        server.mail(email)

        # 3. Test du destinataire
        code, message = server.rcpt(email)
        server.quit()

        # Vérification du code de réponse
        if code == 250:
            print(f"✅ L'adresse '{email}' EXISTE.")

            # Enregistrement dans le fichier texte (mode append 'a')
            with open(FICHIER_RESULTATS, "a", encoding="utf-8") as f:
                f.write(f"{email}\n")
            print(f"💾 Enregistré dans {FICHIER_RESULTATS}")

        else:
            raison = message.decode('utf-8', errors='ignore')
            print(f"❌ L'adresse '{email}' N'EXISTE PAS (Code : {code} - {raison})")

    except (dns.resolver.Timeout, dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        print(f"⚡ Erreur DNS rapide : Impossible de trouver le serveur MX pour {domaine}.")
    except (smtplib.SMTPConnectError, TimeoutError, socket.timeout if 'socket' in locals() else Exception) as e:
        print(f"⚡ Connexion impossible ou expirée (Timeout) pour {email}.")
    except Exception as e:
        print(f"⚠️ Erreur : {e}")


ascii_banner = pyfiglet.figlet_format('Name2Mail', font="slant")
print("\n", "-"*100, "\n")
print(ascii_banner)
print("Un tools orientés OSINT fait pour générer des mails, en fonction des informations fournies par Vous! "
      "\nVous récupérer toutes les informations dans info.txt"
      "\nCréer par théorick")
print("\n", "-"*100, "\n")

def run(playwright: Playwright) -> None:
    emails_list = ["hotmail.com", "outlook.com", "gmail.com", 'yahoo.com', 'protonmail.com']

    nom = str(input('Prenom et Nom a rechercher : '))
    info_spmt = str(input('Information a rechercher : '))
    nom_fichier = 'info.txt'
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    url2 = f"https://www.ecosia.org/search?method=index&q=test"
    page.goto(url2)

    try:
        page.get_by_role("button", name="Tout accepter").click()
    except:
        print()
    while True:
        email_empty = 0
      for email in emails_list:
          url2 = f"https://www.ecosia.org/search?method=index&q={nom.replace(" ", "+")}+{info_spmt.replace(" ", "+")}+intext:\"{email}\""

          #print(url2)
          page.goto(url2)


          # Récupérer le HTML de la page
          html_content = page.content()

          # Parser le HTML avec BeautifulSoup
          soup1 = BeautifulSoup(html_content, 'html.parser')

          try:
              set_emails = set()

              # Parcourir toutes les balises contenant des classes
              for element in soup1.find_all(class_=True):
                  # Extraire le texte de chaque élément
                  text = element.get_text()
                  # Trouver et ajouter les emails uniques dans set_emails
                  emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                  for email in emails:
                      set_emails.add(email)
              if list(set_emails) == []:
                  email_empty = email_empty + 1
                  print("Email empty : ", email_empty)
                  time.sleep(2)
              else:

                  emails_list  = list(set_emails)

                  for i in emails_list:

                      print(i)
                      time.sleep(1)

                  email_empty = 0
          except AttributeError:
              emails = '*'
              print("Email pas trouver")
          for email in list(set_emails):
                verifier_existence_email(email)

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)


