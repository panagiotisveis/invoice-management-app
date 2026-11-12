import streamlit as st
import pandas as pd
import os
import altair as alt
from datetime import datetime, date

st.set_page_config(page_title="Worldwide Αξεσουάρ", layout="centered")

# --- CUSTOM CSS ---

st.markdown("""
<style>
/* Απόκρυψη μενού, header και footer του Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none !important;}

/* Απόκρυψη του εικονιδίου/badge κάτω δεξιά */
[data-testid="stStatusWidget"] {
    display: none !important;
}
.viewerBadge_container__1QSob, 
iframe[title="Streamlit status widget"] {
    display: none !important;
}
footer::after {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
button {
    border-radius: 6px !important;
    min-height: 52px !important;
    font-weight: 600 !important;
}
button[kind="primary"] {
    background-color: #2e7d32 !important;
    color: white !important;
    border: none !important;
}
div[data-testid="stAppViewBlockContainer"] > div > div > div > div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(2) button,
div[data-testid="stAppViewBlockContainer"] > div > div > div > div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(3) button,
div[data-testid="stAppViewBlockContainer"] > div > div > div > div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(4) button {
    background-color: #1976D2 !important; 
    color: white !important;
    border: none !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important; 
}
</style>
""", unsafe_allow_html=True)

DB_CLIENTS = "clients.csv"
DB_SESSIONS = "sessions.csv"
DB_EXPENSES = "expenses.csv"
DB_INVOICES = "invoices.csv"
UPLOAD_DIR = "uploads"
INVOICES_DIR = "invoices_html" 

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(INVOICES_DIR, exist_ok=True)

MONTHS_LIST = [
    "Όλοι", "1 - Ιανουάριος", "2 - Φεβρουάριος", "3 - Μάρτιος", "4 - Απρίλιος",
    "5 - Μάιος", "6 - Ιούνιος", "7 - Ιούλιος", "8 - Αύγουστος",
    "9 - Σεπτέμβριος", "10 - Οκτώβριος", "11 - Νοέμβριος", "12 - Δεκέμβριος"
]

SERVICE_TRANSLATIONS = {
    "Μαθήματα Ελληνικών": "Cours de Grec",
    "Σχολικά Clubs": "Clubs Scolaires / Prestations Parascolaires",
    "Συμβουλευτική (SEL)": "Consultation (SEL)"
}

# --- ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ ---
def format_money(val):
    try:
        if pd.isna(val) or str(val).strip() == "": return ""
        return f"{float(val):.2f}"
    except ValueError: return str(val)

def load_clients():
    if os.path.exists(DB_CLIENTS): 
        df = pd.read_csv(DB_CLIENTS, dtype={'Τηλέφωνο 1': str, 'Τηλέφωνο 2': str, 'Τηλέφωνο': str})
        
        if "Τύπος" not in df.columns: df["Τύπος"] = "Κανονικός"
        if "Φάκελος" not in df.columns: df["Φάκελος"] = ""
        if "Όνομα Παιδιού" not in df.columns: df["Όνομα Παιδιού"] = ""
        if "Όνομα Γονέα 1" not in df.columns: df["Όνομα Γονέα 1"] = df.get("Όνομα Απόδειξης", "")
        if "Όνομα Γονέα 2" not in df.columns: df["Όνομα Γονέα 2"] = ""
        if "Διεύθυνση" not in df.columns: df["Διεύθυνση"] = ""
        if "Τηλέφωνο 1" not in df.columns: df["Τηλέφωνο 1"] = df.get("Τηλέφωνο", "")
        if "Τηλέφωνο 2" not in df.columns: df["Τηλέφωνο 2"] = ""
        if "Email 1" not in df.columns: df["Email 1"] = df.get("Email", "")
        if "Email 2" not in df.columns: df["Email 2"] = ""
        if "Υπηρεσία Γαλλικά" not in df.columns: df["Υπηρεσία Γαλλικά"] = ""
        if "Σημειώσεις" not in df.columns: df["Σημειώσεις"] = ""
        if "Κατάσταση Πελάτη" not in df.columns: df["Κατάσταση Πελάτη"] = "Ενεργός"
        if "Αριθμός Παιδιών" not in df.columns: df["Αριθμός Παιδιών"] = 0
        if "Τιμή ανά Παιδί" not in df.columns: df["Τιμή ανά Παιδί"] = 0.0
        if "Ποσοστό Σχολείου" not in df.columns: df["Ποσοστό Σχολείου"] = 0.0
        
        df = df.fillna("")
        return df
    
    return pd.DataFrame(columns=[
        "Όνομα Εφαρμογής", "Τύπος", "Φάκελος", "Όνομα Παιδιού", "Όνομα Γονέα 1", "Όνομα Γονέα 2", 
        "Διεύθυνση", "Τηλέφωνο 1", "Τηλέφωνο 2", "Email 1", "Email 2",
        "Τιμή Συνάντησης", "Υπηρεσία", "Υπηρεσία Γαλλικά", "Σημειώσεις",
        "Αριθμός Παιδιών", "Τιμή ανά Παιδί", "Ποσοστό Σχολείου", "Συνολική Οφειλή", "Κατάσταση Πελάτη"
    ])

def load_sessions():
    if os.path.exists(DB_SESSIONS): 
        df = pd.read_csv(DB_SESSIONS)
        if "ID Απόδειξης" not in df.columns: df["ID Απόδειξης"] = ""
        df["ID Απόδειξης"] = df["ID Απόδειξης"].fillna("")
        
        df['Κατάσταση Πληρωμής'] = df['Κατάσταση Πληρωμής'].replace({
            'Εκκρεμεί': '🔴 Εκκρεμεί',
            'Εκκρεμεί (Εκτός / Δώρο)': '🟠 Εκκρεμεί (Promo / Pro Bono)',
            '🟠 Εκκρεμεί (Εκτός / Δώρο)': '🟠 Εκκρεμεί (Promo / Pro Bono)',
            'Εξοφλήθηκε': '🟢 Εξοφλήθηκε',
            'Εξοφλήθηκε (Εκτός / Δώρο)': '🟣 Ολοκληρώθηκε (Promo / Pro Bono)',
            '🟣 Εξοφλήθηκε (Εκτός / Δώρο)': '🟣 Ολοκληρώθηκε (Promo / Pro Bono)'
        })
        df['Κατάσταση Πληρωμής'] = df['Κατάσταση Πληρωμής'].apply(lambda x: x if pd.isna(x) else str(x).replace('🔴 🔴', '🔴').replace('🟠 🟠', '🟠').replace('🟢 🟢', '🟢').replace('🟣 🟣', '🟣'))
        
        return df
    return pd.DataFrame(columns=["Πελάτης", "Ημερομηνία", "Κατάσταση Ραντεβού", "Ποσό", "Κατάσταση Πληρωμής", "ID Απόδειξης"])

def load_expenses():
    if os.path.exists(DB_EXPENSES): return pd.read_csv(DB_EXPENSES)
    return pd.DataFrame(columns=["Ημερομηνία", "Είδος Εξόδου", "Ποσό (CHF)", "Σημειώσεις", "Αρχείο Απόδειξης"])

def load_invoices():
    if os.path.exists(DB_INVOICES): return pd.read_csv(DB_INVOICES, dtype={'ID Απόδειξης': str})
    return pd.DataFrame(columns=["ID Απόδειξης", "Όνομα Απόδειξης", "Ημερομηνία Έκδοσης", "Συνολικό Ποσό (CHF)", "Κατάσταση"])

# ==========================================
# ΣΥΣΤΗΜΑ ΑΣΦΑΛΕΙΑΣ (LOGIN)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Είσοδος Συστήματος")
    st.write("Παρακαλώ εισάγετε τον κωδικό πρόσβασης για να συνεχίσετε.")
    
    pwd = st.text_input("Κωδικός Πρόσβασης", type="password")
    if st.button("Είσοδος", type="primary", use_container_width=True):
        if pwd == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Λάθος κωδικός πρόσβασης! Προσπαθήστε ξανά.")
    st.stop() 

def apply_color_status(df):
    def color_rule(val):
        val_str = str(val)
        if '🔴' in val_str: return 'color: #ff4b4b; font-weight: bold;'
        elif '🟠' in val_str: return 'color: #ff9800; font-weight: bold;'
        elif '🟢' in val_str: return 'color: #00c04b; font-weight: bold;'
        elif '🟣' in val_str: return 'color: #9c27b0; font-weight: bold;' 
        return ''
        
    styled = df.style
    if 'Κατάσταση Πληρωμής' in df.columns:
        styled = styled.map(color_rule, subset=['Κατάσταση Πληρωμής']) if hasattr(styled, 'map') else styled.applymap(color_rule, subset=['Κατάσταση Πληρωμής'])
    if 'Κατάσταση' in df.columns:
        def inv_color(v):
            v_str = str(v)
            if v_str == 'Εκκρεμεί': return 'color: #ff4b4b; font-weight: bold;'
            if v_str == 'Εξοφλήθηκε': return 'color: #00c04b; font-weight: bold;'
            return ''
        styled = styled.map(inv_color, subset=['Κατάσταση']) if hasattr(styled, 'map') else styled.applymap(inv_color, subset=['Κατάσταση'])
        
    formatter = {}
    if 'Ποσό' in df.columns: formatter['Ποσό'] = format_money
    if 'Συνολικό Ποσό (CHF)' in df.columns: formatter['Συνολικό Ποσό (CHF)'] = format_money
    return styled.format(formatter)

if "current_page" not in st.session_state: st.session_state.current_page = "home"
if "selected_client_index" not in st.session_state: st.session_state.selected_client_index = None

# ==========================================
# POPUPS ΕΝΕΡΓΕΙΩΝ & ΕΠΙΒΕΒΑΙΩΣΕΩΝ
# ==========================================
@st.dialog("👁️ Προβολή Αποδεικτικού")
def view_receipt_dialog(filepath):
    if not os.path.exists(filepath):
        st.error("Το αρχείο δεν βρέθηκε.")
        return
    ext = filepath.split(".")[-1].lower()
    if ext in ["png", "jpg", "jpeg"]:
        st.image(filepath, use_container_width=True)
        with open(filepath, "rb") as f:
            st.download_button("📥 Λήψη Αρχείου", f.read(), file_name=os.path.basename(filepath), use_container_width=True)
    else:
        st.info(f"Το αρχείο είναι μορφής .{ext.upper()} και δεν μπορεί να προβληθεί απευθείας. Πατήστε παρακάτω για λήψη.")
        with open(filepath, "rb") as f:
            st.download_button("📥 Λήψη Αρχείου", f.read(), file_name=os.path.basename(filepath), type="primary", use_container_width=True)

@st.dialog("⚠️ Επιβεβαίωση Έκδοσης Απόδειξης (Συνοπτική)")
def confirm_issue_invoice_dialog(selected_indices, app_name, total_amt):
    df_inv = load_invoices()
    df_s = load_sessions()
    df_c = load_clients()
    
    client_row = df_c[df_c["Όνομα Εφαρμογής"] == app_name].iloc[0] if len(df_c[df_c["Όνομα Εφαρμογής"] == app_name]) > 0 else None
    if client_row is None:
        st.error("Δεν βρέθηκαν τα στοιχεία του πελάτη.")
        return
    
    parent1 = client_row.get("Όνομα Γονέα 1", "")
    parent2 = client_row.get("Όνομα Γονέα 2", "")
    child_name = client_row.get("Όνομα Παιδιού", "")
    address = client_row.get("Διεύθυνση", "")
    tel1 = client_row.get("Τηλέφωνο 1", "")
    tel2 = client_row.get("Τηλέφωνο 2", "")
    email1 = client_row.get("Email 1", "")
    email2 = client_row.get("Email 2", "")
    
    receipt_name = parent1
    if parent2: receipt_name += f" & {parent2}"
    if not receipt_name: receipt_name = app_name 
    
    st.write(f"Θα εκδοθεί απόδειξη για: **{receipt_name}**")
    st.write(f"Συνολικό Ποσό: **{format_money(total_amt)} CHF**")
    
    c1, c2 = st.columns(2)
    if c1.button("✅ Ναι, Έκδοση", type="primary", use_container_width=True):
        inv_num = len(df_inv) + 1
        inv_id = f"#{inv_num:03d}"
        
        new_inv = pd.DataFrame([{
            "ID Απόδειξης": inv_id,
            "Όνομα Απόδειξης": receipt_name,
            "Ημερομηνία Έκδοσης": date.today().strftime("%d/%m/%Y"),
            "Συνολικό Ποσό (CHF)": total_amt,
            "Κατάσταση": "Εκκρεμεί"
        }])
        df_inv = pd.concat([df_inv, new_inv], ignore_index=True)
        df_inv.to_csv(DB_INVOICES, index=False)
        
        df_s.loc[selected_indices, "ID Απόδειξης"] = inv_id
        df_s.to_csv(DB_SESSIONS, index=False)
        
        service_name_gr = client_row.get("Υπηρεσία", "")
        service_name_fr = client_row.get("Υπηρεσία Γαλλικά", "")
        if not service_name_fr: service_name_fr = SERVICE_TRANSLATIONS.get(service_name_gr, service_name_gr)
        
        dates_list = df_s.loc[selected_indices, "Ημερομηνία"].tolist()
        qty = len(dates_list)
        
        dates_html = ""
        for d in dates_list:
            dates_html += f'<span style="display: inline-block; background-color: #e9ecef; border-radius: 4px; padding: 2px 6px; margin: 2px 4px 2px 0; font-size: 11px; color: #495057; border: 1px solid #dee2e6;">{d}</span>'
        
        unit_price = total_amt / qty if qty > 0 else 0
        
        html_items = f"""
        <tr>
            <td style="border-bottom: 1px solid #eee; padding: 10px; font-size: 13px;">
                <strong>{service_name_fr}</strong><br>
                <div style="margin-top: 5px;">{dates_html}</div>
            </td>
            <td style="border-bottom: 1px solid #eee; padding: 10px; text-align: center; font-size: 13px; vertical-align: top;">{qty}</td>
            <td style="border-bottom: 1px solid #eee; padding: 10px; text-align: right; font-size: 13px; vertical-align: top;">{format_money(unit_price)}</td>
            <td style="border-bottom: 1px solid #eee; padding: 10px; text-align: right; font-size: 13px; vertical-align: top;"><strong>{format_money(total_amt)}</strong></td>
        </tr>
        """
            
        title_fr = "FACTURE"
        
        addr_html = f"{address}<br>" if address else ""
        
        contact_info = []
        if tel1 and tel2: contact_info.append(f"Tél: {tel1} | {tel2}")
        elif tel1: contact_info.append(f"Tél: {tel1}")
        elif tel2: contact_info.append(f"Tél: {tel2}")
        
        if email1 and email2: contact_info.append(f"Email: {email1} | {email2}")
        elif email1: contact_info.append(f"Email: {email1}")
        elif email2: contact_info.append(f"Email: {email2}")
            
        contact_html = "<br>".join(contact_info) + "<br>" if contact_info else ""
        
        child_html = f"<br><em>Concerne : {child_name}</em>" if child_name.strip() else ""
            
        html_receipt = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="utf-8">
            <title>Facture {inv_id.replace('#', '')}</title>
            <style>
                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; line-height: 1.4; margin: 0; padding: 15px; background-color: #f4f4f4; }}
                .invoice-box {{ max-width: 800px; margin: auto; padding: 25px 35px; background: #fff; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                .header-table {{ width: 100%; margin-bottom: 20px; }}
                .header-table td {{ vertical-align: top; }}
                .company-details {{ font-size: 12px; color: #444; }}
                .company-name {{ font-size: 15px; font-weight: bold; color: #111; margin-bottom: 3px; }}
                .invoice-title {{ font-size: 20px; font-weight: bold; letter-spacing: 1px; color: #111; text-align: right; text-transform: uppercase; }}
                .invoice-meta {{ text-align: right; margin-top: 5px; font-size: 13px; }}
                .client-box {{ margin-top: 15px; padding: 12px 15px; background: #fafafa; border-left: 4px solid #555; font-size: 14px; line-height: 1.5; }}
                .items-table {{ width: 100%; border-collapse: collapse; margin-top: 25px; }}
                .items-table th {{ background: #f9f9f9; border-bottom: 2px solid #333; padding: 10px; text-align: left; font-size: 12px; text-transform: uppercase; color: #555; }}
                .items-table th.center {{ text-align: center; }}
                .items-table th.right {{ text-align: right; }}
                .totals-table {{ width: 300px; float: right; border-collapse: collapse; margin-top: 20px; font-size: 13px; }}
                .totals-table td {{ padding: 8px 10px; text-align: right; border-bottom: 1px solid #eee; }}
                .totals-table .net-total {{ font-weight: bold; font-size: 16px; border-bottom: 2px solid #333; color: #111; padding-top: 12px; }}
                .footer {{ clear: both; margin-top: 50px; font-size: 12px; color: #666; }}
                .bank-details {{ margin-top: 15px; padding: 15px; border: 1px solid #ddd; background: #fdfdfd; font-size: 12px; line-height: 1.6; }}
                .thank-you {{ text-align: center; margin-top: 25px; font-style: italic; font-size: 12px; color: #555; }}
            </style>
        </head>
        <body>
            <div class="invoice-box">
                <table class="header-table">
                    <tr>
                        <td class="company-details">
                            <div class="company-name">Iliana Dimitra Tzanetoulakou</div>
                            Services Éducatifs, de Conseil et d'Accompagnement<br>
                            Chemin de la Brume 7, 1110 Morges, VD<br>
                            Tél: +41 76 732 11 94 | Email: hello@heliacounselling.com<br>
                            <strong>IDE:</strong> CHE-341.730.310
                        </td>
                        <td>
                            <div class="invoice-title">{title_fr}</div>
                            <div class="invoice-meta">
                                <strong>N° de facture :</strong> {inv_id.replace('#', '')}<br>
                                <strong>Date d'émission :</strong> {date.today().strftime('%d/%m/%Y')}
                            </div>
                        </td>
                    </tr>
                </table>
                
                <div class="client-box">
                    <strong>À l'attention de :</strong><br>
                    {receipt_name}<br>
                    {addr_html}
                    {contact_html}
                    {child_html}
                </div>
                
                <table class="items-table">
                    <tr>
                        <th>Description des prestations</th>
                        <th class="center">Qté</th>
                        <th class="right">Prix Unitaire</th>
                        <th class="right">Total (CHF)</th>
                    </tr>
                    {html_items}
                </table>
                
                <table class="totals-table">
                    <tr>
                        <td>Montant Total Brut</td>
                        <td>{format_money(total_amt)}</td>
                    </tr>
                    <tr>
                        <td>TVA (Non applicable)</td>
                        <td>0.00</td>
                    </tr>
                    <tr>
                        <td class="net-total">MONTANT TOTAL NET À PAYER</td>
                        <td class="net-total">{format_money(total_amt)}</td>
                    </tr>
                </table>
                
                <div class="footer">
                    <p style="margin-bottom: 5px;"><strong>Conditions de paiement :</strong> Payable à 15 jours.</p>
                    
                    <div class="bank-details">
                        <strong>Coordonnées Bancaires & Paiement</strong><br>
                        <strong>Banque :</strong> UBS Switzerland | <strong>Titulaire :</strong> Tzanetoulakou Iliana Dimitra<br>
                        <strong>IBAN :</strong> CH27 0024 3243 6445 0940 T<br>
                        <strong>TWINT :</strong> +41 76 732 11 94 (Paiement accepté)
                    </div>
                    
                    <div class="thank-you">
                        TVA non applicable conformément à l'art. 10 LTVA (Chiffre d'affaires inférieur à CHF 100'000.-).<br>
                        Merci de votre confiance.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        safe_inv_id = inv_id.replace('#', '')
        file_path = os.path.join(INVOICES_DIR, f"{safe_inv_id}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_receipt)
            
        st.session_state["invoice_created_success"] = True
        st.rerun()
        
    if c2.button("❌ Ακύρωση", use_container_width=True): st.rerun()

@st.dialog("⚠️ Επιβεβαίωση Εξόφλησης")
def confirm_pay_invoice_dialog(inv_id, inv_name, inv_amt):
    st.write(f"Θα σημειώσετε την απόδειξη **{inv_id}** του/της **{inv_name}** ως εξοφλημένη.")
    st.write(f"Ποσό: **{format_money(inv_amt)} CHF**")
    
    c1, c2 = st.columns(2)
    if c1.button("✅ Ναι, Εξοφλήθηκε", type="primary", use_container_width=True):
        df_inv = load_invoices()
        df_s = load_sessions()
        df_c = load_clients()
        
        df_inv.loc[df_inv["ID Απόδειξης"] == inv_id, "Κατάσταση"] = "Εξοφλήθηκε"
        df_inv.to_csv(DB_INVOICES, index=False)
        
        mask_s = df_s["ID Απόδειξης"] == inv_id
        df_s.loc[mask_s, "Κατάσταση Πληρωμής"] = "🟢 Εξοφλήθηκε"
        df_s.to_csv(DB_SESSIONS, index=False)
        
        paid_sessions = df_s[mask_s]
        for _, p_row in paid_sessions.iterrows():
            app_name = p_row["Πελάτης"]
            amt = float(p_row["Ποσό"])
            if app_name in df_c["Όνομα Εφαρμογής"].values:
                c_idx = df_c.index[df_c["Όνομα Εφαρμογής"] == app_name].tolist()[0]
                df_c.at[c_idx, "Συνολική Οφειλή"] = max(0.0, float(df_c.at[c_idx, "Συνολική Οφειλή"]) - amt)
        df_c.to_csv(DB_CLIENTS, index=False)
        st.rerun()
    if c2.button("❌ Ακύρωση", use_container_width=True): st.rerun()

@st.dialog("ΠΡΟΣΘΗΚΗ ΣΤΟ ΠΕΛΑΤΟΛΟΓΙΟ")
def add_client_dialog():
    client_type = st.radio("Επιλογή:", [
        "👤 Ενήλικας Πελάτης (Ιδιαίτερο)", 
        "👦 Παιδί / Μαθητής (Ιδιαίτερο)", 
        "📁 Φάκελος / Club (Ομαδικό)"
    ])
    st.write("---")
    
    if client_type == "📁 Φάκελος / Club (Ομαδικό)":
        folder_name = st.text_input("Όνομα Φακέλου")
        
        selected_service = st.selectbox("Είδος Υπηρεσίας", ["Σχολικά Clubs", "Μαθήματα Ελληνικών", "Συμβουλευτική (SEL)", "Άλλο..."], index=0)
        final_service = ""
        final_service_fr = ""
        if selected_service == "Άλλο...": 
            final_service = st.text_input("Νέα υπηρεσία (Ελληνικά)")
            final_service_fr = st.text_input("Νέα υπηρεσία (Γαλλικά)")
        else:
            final_service = selected_service
            final_service_fr = SERVICE_TRANSLATIONS.get(selected_service, selected_service)
            
        price_str = st.text_input("Τιμή ανά Μαθητή (CHF)", value="30.0")
        try: final_price = float(price_str.replace(",", ".")) if price_str else 0.0
        except ValueError: final_price = 0.0
            
        if st.button("✅ Δημιουργία & Μετάβαση", type="primary", use_container_width=True):
            if folder_name and final_service:
                new_client = pd.DataFrame([{
                    "Όνομα Εφαρμογής": folder_name, "Τύπος": "Φάκελος", "Φάκελος": "",
                    "Όνομα Παιδιού": "", "Όνομα Γονέα 1": "", "Όνομα Γονέα 2": "", 
                    "Διεύθυνση": "", "Τηλέφωνο 1": "", "Τηλέφωνο 2": "", "Email 1": "", "Email 2": "",
                    "Τιμή Συνάντησης": final_price, "Υπηρεσία": final_service, "Υπηρεσία Γαλλικά": final_service_fr, "Σημειώσεις": "",
                    "Αριθμός Παιδιών": 0, "Τιμή ανά Παιδί": 0.0, "Ποσοστό Σχολείου": 0.0,
                    "Συνολική Οφειλή": 0.0, "Κατάσταση Πελάτη": "Ενεργός"
                }])
                df_c = load_clients()
                new_idx = len(df_c)
                df_new = pd.concat([df_c, new_client], ignore_index=True)
                df_new.to_csv(DB_CLIENTS, index=False)
                
                st.session_state.selected_client_index = new_idx
                st.session_state.current_page = "client_profile"
                st.rerun()
            else: st.error("Συμπληρώστε το Όνομα Φακέλου και την Υπηρεσία.")

    elif client_type == "👤 Ενήλικας Πελάτης (Ιδιαίτερο)":
        app_name = st.text_input("Όνομα στην Εφαρμογή")
        parent1 = st.text_input("Όνομα Πελάτη *")
        address = st.text_input("Πλήρης Διεύθυνση")
        
        c1, c2 = st.columns(2)
        with c1: tel1 = st.text_input("Τηλέφωνο 1")
        with c2: email1 = st.text_input("Email 1")
            
        selected_service = st.selectbox("Είδος Υπηρεσίας", ["Μαθήματα Ελληνικών", "Συμβουλευτική (SEL)", "Άλλο..."], index=0)
        final_service = ""
        final_service_fr = ""
        if selected_service == "Άλλο...": 
            final_service = st.text_input("Νέα υπηρεσία (Ελληνικά)")
            final_service_fr = st.text_input("Νέα υπηρεσία (Γαλλικά)")
        else:
            final_service = selected_service
            final_service_fr = SERVICE_TRANSLATIONS.get(selected_service, selected_service)
            
        price_str = st.text_input("Τιμή ανά Συνάντηση (CHF)", value="30.0")
        try: final_price = float(price_str.replace(",", ".")) if price_str else 0.0
        except ValueError: final_price = 0.0
        
        if st.button("✅ Προσθήκη Πελάτη", type="primary", use_container_width=True):
            if app_name and parent1 and final_service:
                new_client = pd.DataFrame([{
                    "Όνομα Εφαρμογής": app_name, "Τύπος": "Κανονικός", "Φάκελος": "",
                    "Όνομα Παιδιού": "", "Όνομα Γονέα 1": parent1, "Όνομα Γονέα 2": "", 
                    "Διεύθυνση": address, "Τηλέφωνο 1": tel1, "Τηλέφωνο 2": "", "Email 1": email1, "Email 2": "",
                    "Τιμή Συνάντησης": final_price, "Υπηρεσία": final_service, "Υπηρεσία Γαλλικά": final_service_fr, "Σημειώσεις": "",
                    "Αριθμός Παιδιών": 0, "Τιμή ανά Παιδί": 0.0, "Ποσοστό Σχολείου": 0.0,
                    "Συνολική Οφειλή": 0.0, "Κατάσταση Πελάτη": "Ενεργός"
                }])
                df_c = load_clients()
                df_new = pd.concat([df_c, new_client], ignore_index=True)
                df_new.to_csv(DB_CLIENTS, index=False)
                st.rerun()
            else: st.error("⚠️ Το Όνομα Εφαρμογής, το Όνομα Πελάτη και η Υπηρεσία είναι υποχρεωτικά.")
            
    else: # 👦 Παιδί / Μαθητής
        app_name = st.text_input("Όνομα στην Εφαρμογή")
        child_name = st.text_input("Όνομα Παιδιού / Μαθητή")
        
        st.markdown("##### 📍 Στοιχεία Τιμολόγησης")
        parent1 = st.text_input("Όνομα Γονέα 1 *")
        parent2 = st.text_input("Όνομα Γονέα 2")
        address = st.text_input("Πλήρης Διεύθυνση")
        
        st.markdown("##### 📞 Επικοινωνία")
        c1, c2 = st.columns(2)
        with c1:
            tel1 = st.text_input("Τηλέφωνο 1")
            email1 = st.text_input("Email 1")
        with c2:
            tel2 = st.text_input("Τηλέφωνο 2")
            email2 = st.text_input("Email 2")
            
        st.markdown("##### 💰 Υπηρεσία & Χρέωση")
        selected_service = st.selectbox("Είδος Υπηρεσίας", ["Μαθήματα Ελληνικών", "Συμβουλευτική (SEL)", "Άλλο..."], index=0)
        final_service = ""
        final_service_fr = ""
        if selected_service == "Άλλο...": 
            final_service = st.text_input("Νέα υπηρεσία (Ελληνικά)")
            final_service_fr = st.text_input("Νέα υπηρεσία (Γαλλικά)")
        else:
            final_service = selected_service
            final_service_fr = SERVICE_TRANSLATIONS.get(selected_service, selected_service)
            
        price_str = st.text_input("Τιμή ανά Συνάντηση (CHF)", value="30.0")
        try: final_price = float(price_str.replace(",", ".")) if price_str else 0.0
        except ValueError: final_price = 0.0
        
        if st.button("✅ Προσθήκη Μαθητή", type="primary", use_container_width=True):
            if app_name and parent1 and final_service:
                new_client = pd.DataFrame([{
                    "Όνομα Εφαρμογής": app_name, "Τύπος": "Κανονικός", "Φάκελος": "",
                    "Όνομα Παιδιού": child_name, "Όνομα Γονέα 1": parent1, "Όνομα Γονέα 2": parent2, 
                    "Διεύθυνση": address, "Τηλέφωνο 1": tel1, "Τηλέφωνο 2": tel2, "Email 1": email1, "Email 2": email2,
                    "Τιμή Συνάντησης": final_price, "Υπηρεσία": final_service, "Υπηρεσία Γαλλικά": final_service_fr, "Σημειώσεις": "",
                    "Αριθμός Παιδιών": 0, "Τιμή ανά Παιδί": 0.0, "Ποσοστό Σχολείου": 0.0,
                    "Συνολική Οφειλή": 0.0, "Κατάσταση Πελάτη": "Ενεργός"
                }])
                df_c = load_clients()
                df_new = pd.concat([df_c, new_client], ignore_index=True)
                df_new.to_csv(DB_CLIENTS, index=False)
                st.rerun()
            else: st.error("⚠️ Το Όνομα Εφαρμογής, το Όνομα Γονέα 1 και η Υπηρεσία είναι υποχρεωτικά.")

@st.dialog("➕ Προσθήκη Μαθητή στο Club")
def add_student_to_club_dialog(folder_name, folder_service, folder_service_fr, default_price):
    app_name = st.text_input("Όνομα στην Εφαρμογή")
    child_name = st.text_input("Όνομα Παιδιού")
    
    st.markdown("##### 📍 Στοιχεία Τιμολόγησης")
    parent1 = st.text_input("Όνομα Γονέα 1 *")
    parent2 = st.text_input("Όνομα Γονέα 2")
    address = st.text_input("Πλήρης Διεύθυνση")
    
    st.markdown("##### 📞 Επικοινωνία")
    c1, c2 = st.columns(2)
    with c1:
        tel1 = st.text_input("Τηλέφωνο 1")
        email1 = st.text_input("Email 1")
    with c2:
        tel2 = st.text_input("Τηλέφωνο 2")
        email2 = st.text_input("Email 2")
        
    price_str = st.text_input("Τιμή ανά Συνάντηση (CHF)", value=str(default_price))
    try: final_price = float(price_str.replace(",", ".")) if price_str else 0.0
    except ValueError: final_price = 0.0
    
    if st.button("✅ Αποθήκευση Μαθητή", type="primary", use_container_width=True):
        if app_name and parent1:
            new_client = pd.DataFrame([{
                "Όνομα Εφαρμογής": app_name, "Τύπος": "Μαθητής", "Φάκελος": folder_name,
                "Όνομα Παιδιού": child_name, "Όνομα Γονέα 1": parent1, "Όνομα Γονέα 2": parent2, 
                "Διεύθυνση": address, "Τηλέφωνο 1": tel1, "Τηλέφωνο 2": tel2, "Email 1": email1, "Email 2": email2,
                "Τιμή Συνάντησης": final_price, "Υπηρεσία": folder_service, "Υπηρεσία Γαλλικά": folder_service_fr, "Σημειώσεις": "",
                "Αριθμός Παιδιών": 0, "Τιμή ανά Παιδί": 0.0, "Ποσοστό Σχολείου": 0.0,
                "Συνολική Οφειλή": 0.0, "Κατάσταση Πελάτη": "Ενεργός"
            }])
            df_c = load_clients()
            df_new = pd.concat([df_c, new_client], ignore_index=True)
            df_new.to_csv(DB_CLIENTS, index=False)
            st.rerun()
        else: st.error("⚠️ Το Όνομα Εφαρμογής και το Όνομα Γονέα 1 είναι υποχρεωτικά.")

@st.dialog("📝 Γρήγορη Καταχώρηση Συνεδρίας")
def quick_add_session_dialog():
    df_c = load_clients()
    session_type = st.radio("Είδος Συνεδρίας:", ["Ατομική Συνεδρία", "Ομαδική Συνεδρία (Club)"])
    st.write("---")
    
    if session_type == "Ατομική Συνεδρία":
        df_active = df_c[(df_c["Κατάσταση Πελάτη"] == "Ενεργός") & (df_c["Τύπος"] == "Κανονικός")]
        
        if df_active.empty:
            st.warning("Δεν υπάρχουν ενεργοί μεμονωμένοι πελάτες.")
            return
            
        client_names = df_active['Όνομα Εφαρμογής'].tolist()
        selected_client = st.selectbox("Επιλογή Πελάτη", client_names, index=None, placeholder="Επιλέξτε...")
        
        if selected_client:
            client_row = df_active[df_active['Όνομα Εφαρμογής'] == selected_client].iloc[0]
            form_c1, form_c2 = st.columns(2)
            with form_c1:
                date_input = st.date_input("Ημερομηνία", date.today())
                duration = st.selectbox("Διάρκεια", ["1 ώρα", "1:30", "2 ώρες", "2:30"])
                status = st.selectbox("Κατάσταση", ["Ολοκληρώθηκε", "Ακυρώθηκε Έγκαιρα (50%)", "Ακυρώθηκε Οριακά (100%)"])
            with form_c2:
                base_amt = st.number_input("Αρχικό Ποσό", value=float(client_row['Τιμή Συνάντησης']), step=5.0)
                payment_base = st.selectbox("Πληρωμή", ["🔴 Εκκρεμεί", "🟢 Εξοφλήθηκε"], index=0)
                
            with st.container(border=True):
                st.markdown("<h6 style='color: #ff9800; margin-bottom: 5px;'>🟠 Promo / Pro Bono</h6>", unsafe_allow_html=True)
                is_gift = st.checkbox("Καταχώρηση ως δωρεάν παροχή (δεν τιμολογείται)")
                
            if is_gift:
                if "Εκκρεμεί" in payment_base: payment = "🟠 Εκκρεμεί (Promo / Pro Bono)"
                else: payment = "🟣 Ολοκληρώθηκε (Promo / Pro Bono)"
            else:
                payment = payment_base
            
            multiplier = {"1 ώρα": 1.0, "1:30": 1.5, "2 ώρες": 2.0, "2:30": 2.5}[duration]
            final_amt = base_amt * multiplier
            if status == "Ακυρώθηκε Έγκαιρα (50%)": final_amt = final_amt * 0.5
            st.info(f"💰 **Τελικό Ποσό:** {format_money(final_amt)} CHF")
            
            def save_sess(update_base=False):
                new_session = pd.DataFrame([{"Πελάτης": selected_client, "Ημερομηνία": date_input.strftime("%d/%m/%Y"), "Κατάσταση Ραντεβού": status, "Ποσό": final_amt, "Κατάσταση Πληρωμής": payment, "ID Απόδειξης": ""}])
                df_s = load_sessions()
                df_s = pd.concat([df_s, new_session], ignore_index=True)
                df_s.to_csv(DB_SESSIONS, index=False)
                
                if "🔴 Εκκρεμεί" in payment or "🟠 Εκκρεμεί" in payment:
                    df_c_reload = load_clients()
                    client_idx = df_c_reload.index[df_c_reload['Όνομα Εφαρμογής'] == selected_client].tolist()[0]
                    df_c_reload.at[client_idx, 'Συνολική Οφειλή'] = float(df_c_reload.at[client_idx, 'Συνολική Οφειλή']) + float(final_amt)
                    if update_base: df_c_reload.at[client_idx, 'Τιμή Συνάντησης'] = float(base_amt)
                    df_c_reload.to_csv(DB_CLIENTS, index=False)
                st.rerun()

            if base_amt != float(client_row['Τιμή Συνάντησης']):
                st.warning("⚠️ Αλλάξατε το Αρχικό Ποσό σε σχέση με την προεπιλογή. Πώς θέλετε να το αποθηκεύσετε;")
                b1, b2 = st.columns(2)
                if b1.button("Αποθήκευση & Μόνιμη Ενημέρωση", use_container_width=True): save_sess(True)
                if b2.button("Μόνο για αυτή τη φορά", type="primary", use_container_width=True): save_sess(False)
            else:
                if st.button("💾 Αποθήκευση Συνεδρίας", type="primary", use_container_width=True): save_sess(False)
                
    else: # Ομαδική
        df_folders = df_c[(df_c["Κατάσταση Πελάτη"] == "Ενεργός") & (df_c["Τύπος"] == "Φάκελος")]
        if df_folders.empty:
            st.warning("Δεν υπάρχουν ενεργά Clubs.")
            return
            
        club_names = df_folders['Όνομα Εφαρμογής'].tolist()
        selected_club = st.selectbox("Επιλογή Club", club_names, index=None, placeholder="Επιλέξτε...")
        
        if selected_club:
            st.info("Για την ομαδική καταχώρηση θα μεταφερθείτε στη διαχείριση του Club.")
            if st.button("🚀 Μετάβαση για Καταχώρηση", type="primary", use_container_width=True):
                club_idx = df_c.index[df_c['Όνομα Εφαρμογής'] == selected_club].tolist()[0]
                st.session_state.selected_client_index = club_idx
                st.session_state.current_page = "client_profile"
                st.session_state[f"group_session_mode_{club_idx}"] = True
                st.rerun()

@st.dialog("📉 Καταχώρηση Νέου Εξόδου")
def add_expense_dialog():
    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("Ημερομηνία", date.today())
        expense_type_choice = st.selectbox("Είδος Εξόδου", ["Αναλώσιμα / Γραφική Ύλη", "Λογισμικά / Συνδρομές", "Μετακινήσεις (Βενζίνη, Εισιτήρια)", "Ενοίκιο / Προμήθεια Σχολείου", "Εξοπλισμός", "Άλλο..."], index=None, placeholder="Επιλέξτε...")
        if expense_type_choice == "Άλλο...": expense_type = st.text_input("Διευκρινίστε το είδος:")
        else: expense_type = expense_type_choice
    with col2:
        amount = st.number_input("Ποσό (CHF)", min_value=0.0, step=5.0)
        notes = st.text_input("Σημειώσεις")
    st.write("---")
    uploaded_file = st.file_uploader("📸 Προσθήκη Αποδεικτικού", type=["pdf", "png", "jpg", "jpeg", "docx", "doc"])
    st.divider()
    btn_c1, btn_c2 = st.columns(2)
    if btn_c1.button("✅ Αποθήκευση Εξόδου", type="primary", use_container_width=True):
        if expense_type and amount > 0:
            filename = "-"
            if uploaded_file is not None:
                timestamp = date.today().strftime("%Y%m%d")
                safe_name = f"{timestamp}_{uploaded_file.name}"
                file_path = os.path.join(UPLOAD_DIR, safe_name)
                with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
                filename = safe_name
            new_expense = pd.DataFrame([{"Ημερομηνία": date_input.strftime("%d/%m/%Y"), "Είδος Εξόδου": expense_type, "Ποσό (CHF)": amount, "Σημειώσεις": notes, "Αρχείο Απόδειξης": filename}])
            df_e = load_expenses()
            df_e = pd.concat([df_e, new_expense], ignore_index=True)
            df_e.to_csv(DB_EXPENSES, index=False)
            st.rerun()
        else: st.error("⚠️ Συμπληρώστε το Είδος και το Ποσό (πρέπει να είναι μεγαλύτερο του μηδενός).")
    if btn_c2.button("❌ Ακύρωση", use_container_width=True): st.rerun()

# ==========================================
# ΣΕΛΙΔΑ 1: ΑΡΧΙΚΗ ΣΕΛΙΔΑ (DASHBOARD)
# ==========================================
def show_home_page():
    st.title("🌻Worldwide Αξεσουάρ🌻")

    st.markdown("##### 📌 Πλοήγηση")
    nav_c1, nav_c2, nav_c3, nav_c4 = st.columns(4)
    with nav_c1:
        if st.button("👥 Πελατολόγιο", use_container_width=True): st.session_state.current_page = "clients_list"; st.rerun()
    with nav_c2:
        if st.button("📅 Συνεδρίες", use_container_width=True): st.session_state.current_page = "all_sessions"; st.rerun()
    with nav_c3:
        if st.button("📉 Έξοδα", use_container_width=True): st.session_state.current_page = "expenses_list"; st.rerun()
    with nav_c4:
        if st.button("📊 Στατιστικά", use_container_width=True): st.session_state.current_page = "statistics_page"; st.rerun()

    st.write("")
    st.markdown("##### ⚡ Γρήγορες Ενέργειες")
    act_row1_col1, act_row1_col2 = st.columns(2)
    with act_row1_col1:
        if st.button("➕ Νέος Πελάτης / Φάκελος", type="primary", use_container_width=True): add_client_dialog()
    with act_row1_col2:
        if st.button("📝 Νέα Συνεδρία", type="primary", use_container_width=True): quick_add_session_dialog()
        
    act_row2_col1, act_row2_col2 = st.columns(2)
    with act_row2_col1:
        if st.button("💸 Νέο Έξοδο", type="primary", use_container_width=True): add_expense_dialog()
    with act_row2_col2:
        if st.button("🧾 Αποδείξεις", type="primary", use_container_width=True): st.session_state.current_page = "invoices_page"; st.rerun()

    st.write("---")
    st.subheader("🔴 Ανεξόφλητες Αποδείξεις")
    df_inv = load_invoices()
    
    if df_inv.empty: st.info("Δεν έχουν εκδοθεί αποδείξεις ακόμα.")
    else:
        df_inv_pending = df_inv[df_inv["Κατάσταση"] == "Εκκρεμεί"].copy()
        df_inv_pending = df_inv_pending.sort_values(by="ID Απόδειξης", ascending=False)
        if df_inv_pending.empty: st.success("Όλες οι εκδοθείσες αποδείξεις έχουν πληρωθεί! 🎉")
        else:
            for idx, row in df_inv_pending.iterrows():
                with st.container(border=True):
                    col_info, col_btn = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"**{row['Όνομα Απόδειξης']}** — {format_money(row['Συνολικό Ποσό (CHF)'])} CHF")
                        st.caption(f"ID: {row['ID Απόδειξης']} | Ημ/νία: {row['Ημερομηνία Έκδοσης']}")
                    with col_btn:
                        if st.button("✅ Εξόφληση", key=f"home_pay_{row['ID Απόδειξης']}", type="primary", use_container_width=True):
                            confirm_pay_invoice_dialog(row['ID Απόδειξης'], row['Όνομα Απόδειξης'], row['Συνολικό Ποσό (CHF)'])
                        file_p = os.path.join(INVOICES_DIR, f"{row['ID Απόδειξης'].replace('#','')}.html")
                        if os.path.exists(file_p):
                            with open(file_p, "r", encoding="utf-8") as f: html_data = f.read()
                            st.download_button("📄 Λήψη", data=html_data, file_name=f"Invoice_{row['Όνομα Απόδειξης']}_{row['ID Απόδειξης']}.html", mime="text/html", key=f"dl_home_{row['ID Απόδειξης']}", use_container_width=True)
    
    st.write("---")
    st.subheader("🔴 Εκκρεμείς Συνεδρίες (Επίσημες & Promo)")
    df_s = load_sessions()
    
    if df_s.empty: st.info("Δεν έχουν καταχωρηθεί συνεδρίες ακόμα.")
    else:
        df_pend_home = df_s[df_s["Κατάσταση Πληρωμής"].str.contains("Εκκρεμεί")].copy()
        if df_pend_home.empty: st.success("Δεν υπάρχουν εκκρεμείς συνεδρίες. Όλα καθαρά! 🎉")
        else:
            df_pend_home['orig_id'] = df_pend_home.index
            df_pend_home['sort_date'] = pd.to_datetime(df_pend_home['Ημερομηνία'], format="%d/%m/%Y", errors='coerce')
            df_pend_home = df_pend_home.sort_values(by=['sort_date', 'orig_id'], ascending=[False, False]).drop(columns=['sort_date', 'orig_id'])
            display_df = df_pend_home.drop(columns=["ID Απόδειξης"]) if "ID Απόδειξης" in df_pend_home.columns else df_pend_home
            st.dataframe(apply_color_status(display_df), hide_index=True, use_container_width=True)

# ==========================================
# ΣΕΛΙΔΑ 2: ΑΠΟΔΕΙΞΕΙΣ (ΤΙΜΟΛΟΓΗΣΗ & ΕΞΟΦΛΗΣΗ)
# ==========================================
def show_invoices_page():
    st.title("🧾 Διαχείριση Αποδείξεων")
    if st.button("🔙 Επιστροφή στο Κεντρικό Μενού", use_container_width=True):
        st.session_state.current_page = "home"; st.rerun()
        
    if st.session_state.get("invoice_created_success"):
        st.toast("✅ Η απόδειξη εκδόθηκε επιτυχώς!", icon="🧾")
        st.session_state["invoice_created_success"] = False
        
    st.write("---")
    
    df_c = load_clients()
    df_s = load_sessions()
    df_inv = load_invoices()
    
    st.markdown("### 📝 Έκδοση Νέας Απόδειξης (Συνοπτική)")
    df_active = df_c[(df_c["Κατάσταση Πελάτη"] == "Ενεργός") & (df_c["Τύπος"] != "Φάκελος")]
    
    if df_active.empty:
        st.warning("Δεν υπάρχουν πελάτες/μαθητές.")
    else:
        client_options = []
        for _, row in df_active.iterrows():
            parent = row.get("Όνομα Γονέα 1", "")
            disp = f"{row['Όνομα Εφαρμογής']} (Πελάτης/Γονέας: {parent})" if parent else row['Όνομα Εφαρμογής']
            client_options.append({"display": disp, "app_name": row["Όνομα Εφαρμογής"]})
            
        selected_disp = st.selectbox("Επιλέξτε Πελάτη / Μαθητή:", [opt["display"] for opt in client_options], index=None, placeholder="Επιλέξτε...")
        
        if selected_disp:
            app_name = next(opt["app_name"] for opt in client_options if opt["display"] == selected_disp)
            
            pending_sessions = df_s[
                (df_s["Πελάτης"] == app_name) & 
                (df_s["Κατάσταση Πληρωμής"] == "🔴 Εκκρεμεί") & 
                (df_s["ID Απόδειξης"] == "")
            ].copy()
            
            if pending_sessions.empty:
                st.info("Δεν υπάρχουν εκκρεμείς (επίσημες) συνεδρίες προς τιμολόγηση για αυτόν τον πελάτη.")
            else:
                st.write(f"Βρέθηκαν **{len(pending_sessions)}** εκκρεμείς συνεδρίες. Επιλέξτε ποιες θα εντάξετε:")
                
                pending_sessions.insert(0, "Επιλογή", True)
                display_pending = pending_sessions.copy()
                display_pending["Ποσό"] = display_pending["Ποσό"].apply(format_money)
                
                edited_sessions = st.data_editor(
                    display_pending, hide_index=True, use_container_width=True,
                    column_config={"Επιλογή": st.column_config.CheckboxColumn("Επιλογή", default=True)},
                    disabled=["Πελάτης", "Ημερομηνία", "Ποσό", "Κατάσταση Πληρωμής", "ID Απόδειξης"]
                )
                
                selected_indices = edited_sessions[edited_sessions["Επιλογή"] == True].index.tolist()
                total_due = pending_sessions.loc[selected_indices, "Ποσό"].astype(float).sum() if len(selected_indices) > 0 else 0.0
                
                st.markdown(f"#### 💰 Συνολικό Ποσό Επιλεγμένων: {format_money(total_due)} CHF")
                
                if st.button("🖨️ Έκδοση Απόδειξης (Aggregated)", type="primary", use_container_width=True):
                    if len(selected_indices) == 0: st.error("Επιλέξτε τουλάχιστον μία συνεδρία.")
                    else: confirm_issue_invoice_dialog(selected_indices, app_name, total_due)

    st.write("---")
    st.markdown("### 🗂️ Ιστορικό & Εξόφληση Αποδείξεων")
    if df_inv.empty: st.info("Δεν έχουν εκδοθεί αποδείξεις ακόμα.")
    else:
        df_inv_pending = df_inv[df_inv["Κατάσταση"] == "Εκκρεμεί"].copy()
        df_inv_pending = df_inv_pending.sort_values(by="ID Απόδειξης", ascending=False)
        
        st.markdown("🔴 **Εκκρεμούν προς Πληρωμή**")
        
        if df_inv_pending.empty: st.success("Όλες οι εκδοθείσες αποδείξεις έχουν πληρωθεί!")
        else:
            for idx, row in df_inv_pending.iterrows():
                with st.container(border=True):
                    col_info, col_btn_group = st.columns([2.5, 1.5])
                    with col_info:
                        st.markdown(f"**{row['Όνομα Απόδειξης']}** — {format_money(row['Συνολικό Ποσό (CHF)'])} CHF")
                        st.caption(f"ID: {row['ID Απόδειξης']} | Ημ/νία: {row['Ημερομηνία Έκδοσης']}")
                    with col_btn_group:
                        b1, b2 = st.columns(2)
                        if b1.button("✅ Εξόφληση", key=f"pay_{row['ID Απόδειξης']}", type="primary"):
                            confirm_pay_invoice_dialog(row['ID Απόδειξης'], row['Όνομα Απόδειξης'], row['Συνολικό Ποσό (CHF)'])
                        file_p = os.path.join(INVOICES_DIR, f"{row['ID Απόδειξης'].replace('#','')}.html")
                        if os.path.exists(file_p):
                            with open(file_p, "r", encoding="utf-8") as f: html_data = f.read()
                            b2.download_button("📄 Λήψη", data=html_data, file_name=f"Invoice_{row['Όνομα Απόδειξης']}_{row['ID Απόδειξης']}.html", mime="text/html", key=f"dl_{row['ID Απόδειξης']}")

        st.write("")
        st.markdown("🟢 **Εξοφλημένες Αποδείξεις**")
        df_inv_paid = df_inv[df_inv["Κατάσταση"] == "Εξοφλήθηκε"].copy()
        df_inv_paid = df_inv_paid.sort_values(by="ID Απόδειξης", ascending=False)
        
        if df_inv_paid.empty: st.info("Καμία εξοφλημένη απόδειξη.")
        else: 
            for idx, row in df_inv_paid.iterrows():
                with st.container(border=True):
                    col_info, col_btn_group = st.columns([2.5, 1.5])
                    with col_info:
                        st.markdown(f"**{row['Όνομα Απόδειξης']}** — :green[{format_money(row['Συνολικό Ποσό (CHF)'])} CHF]")
                        st.caption(f"ID: {row['ID Απόδειξης']} | Ημ/νία: {row['Ημερομηνία Έκδοσης']} | Εξοφλήθηκε")
                    with col_btn_group:
                        file_p = os.path.join(INVOICES_DIR, f"{row['ID Απόδειξης'].replace('#','')}.html")
                        if os.path.exists(file_p):
                            with open(file_p, "r", encoding="utf-8") as f: html_data = f.read()
                            st.download_button("📄 Λήψη Απόδειξης", data=html_data, file_name=f"Invoice_{row['Όνομα Απόδειξης']}_{row['ID Απόδειξης']}.html", mime="text/html", key=f"dl_paid_{row['ID Απόδειξης']}", use_container_width=True)

# ==========================================
# ΣΕΛΙΔΑ 3: ΠΕΛΑΤΟΛΟΓΙΟ (ΦΑΚΕΛΟΙ & ΜΑΘΗΤΕΣ)
# ==========================================
def show_clients_list_page():
    st.title("👥 Πελατολόγιο")
    if st.button("🔙 Επιστροφή στο Κεντρικό Μενού", use_container_width=True): st.session_state.current_page = "home"; st.rerun()
    st.write("---")
    df_clients = load_clients()
    
    df_folders = df_clients[(df_clients["Κατάσταση Πελάτη"] == "Ενεργός") & (df_clients["Τύπος"] == "Φάκελος")]
    df_individuals = df_clients[(df_clients["Κατάσταση Πελάτη"] == "Ενεργός") & (df_clients["Τύπος"] == "Κανονικός")]
    
    st.markdown("### 📁 Φάκελοι / Clubs")
    if df_folders.empty: st.info("Δεν υπάρχουν ομαδικοί φάκελοι.")
    else:
        cols = st.columns(2)
        for i, (index, row) in enumerate(df_folders.iterrows()):
            with cols[i % 2]:
                with st.container(border=True):
                    st.subheader(f"📁 {row['Όνομα Εφαρμογής']}")
                    st.markdown(f"*{row['Υπηρεσία']}*")
                    kids_count = len(df_clients[(df_clients["Φάκελος"] == row['Όνομα Εφαρμογής']) & (df_clients["Κατάσταση Πελάτη"] == "Ενεργός")])
                    st.markdown(f"👥 Ενεργοί Μαθητές: **{kids_count}**")
                    if st.button("📂 Άνοιγμα Φακέλου", key=f"open_folder_{index}", use_container_width=True):
                        st.session_state.selected_client_index = index
                        st.session_state.current_page = "client_profile"
                        st.rerun()
                        
    st.write("---")
    st.markdown("### 👤 Μεμονωμένοι Πελάτες & Μαθητές")
    if df_individuals.empty: st.info("Δεν υπάρχουν μεμονωμένοι πελάτες.")
    else:
        cols = st.columns(2)
        for i, (index, row) in enumerate(df_individuals.iterrows()):
            with cols[i % 2]:
                with st.container(border=True):
                    st.subheader(f"{row['Όνομα Εφαρμογής']}")
                    st.markdown(f"*{row['Υπηρεσία']}*")
                    st.markdown(f"💰 Τιμή: **{format_money(row['Τιμή Συνάντησης'])} CHF/ώρα**")
                    st.markdown(f"⚠️ Οφειλή: **{format_money(row['Συνολική Οφειλή'])} CHF**")
                    if st.button("📂 Άνοιγμα Προφίλ", key=f"open_ind_{index}", use_container_width=True):
                        st.session_state.selected_client_index = index
                        st.session_state.current_page = "client_profile"
                        st.rerun()

def show_client_profile():
    index = st.session_state.selected_client_index
    df_c = load_clients()
    if index not in df_c.index: st.session_state.current_page = "clients_list"; st.rerun()
    row = df_c.loc[index]
    client_name = row['Όνομα Εφαρμογής']
    client_type = row.get('Τύπος', 'Κανονικός')
    
    for key in ["show_session_form", "del_sess_mode", "confirm_del_client", "edit_mode", "group_session_mode"]:
        if f"{key}_{index}" not in st.session_state: st.session_state[f"{key}_{index}"] = False

    t_btn1, t_btn2, t_btn3 = st.columns(3)
    if t_btn1.button("🔙 Πίσω", use_container_width=True): st.session_state.current_page = "clients_list"; st.rerun()
    
    if client_type == "Φάκελος":
        if t_btn2.button("✏️ Επεξεργασία Φακέλου", use_container_width=True):
            st.session_state[f"edit_mode_{index}"] = not st.session_state[f"edit_mode_{index}"]
            st.session_state[f"confirm_del_client_{index}"] = False; st.session_state[f"group_session_mode_{index}"] = False; st.rerun()
        if t_btn3.button("📦 Αρχειοθέτηση Φακέλου", use_container_width=True):
            st.session_state[f"confirm_del_client_{index}"] = not st.session_state[f"confirm_del_client_{index}"]
            st.session_state[f"edit_mode_{index}"] = False; st.session_state[f"group_session_mode_{index}"] = False; st.rerun()
            
        if st.session_state[f"confirm_del_client_{index}"]:
            st.warning("⚠️ Αρχειοθέτηση Φακέλου; (Δεν θα διαγραφούν τα παιδιά, αλλά θα κρυφτεί ο φάκελος).")
            conf1, conf2 = st.columns(2)
            if conf1.button("✅ Ναι, Αρχειοθέτηση", type="primary", use_container_width=True):
                df_c.at[index, 'Κατάσταση Πελάτη'] = "Αρχειοθετημένος"; df_c.to_csv(DB_CLIENTS, index=False)
                st.session_state.current_page = "clients_list"; st.rerun()
            if conf2.button("❌ Ακύρωση", use_container_width=True): st.session_state[f"confirm_del_client_{index}"] = False; st.rerun()

        if st.session_state[f"edit_mode_{index}"]:
            with st.container(border=True):
                edit_app_name = st.text_input("Όνομα Φακέλου", value=row['Όνομα Εφαρμογής'])
                edit_service_txt = st.text_input("Υπηρεσία", value=row['Υπηρεσία'])
                edit_service_fr = st.text_input("Υπηρεσία Γαλλικά", value=row.get('Υπηρεσία Γαλλικά', ''))
                
                price_str = st.text_input("Προεπιλεγμένη Τιμή ανά μαθητή", value=str(row.get('Τιμή Συνάντησης', '30.0')))
                try: edit_price = float(price_str.replace(",", "."))
                except ValueError: edit_price = float(row.get('Τιμή Συνάντησης', 30.0))
                
                if st.button("💾 Αποθήκευση Φακέλου", type="primary", use_container_width=True):
                    df_c.at[index, 'Όνομα Εφαρμογής'] = edit_app_name
                    df_c.at[index, 'Υπηρεσία'] = edit_service_txt
                    df_c.at[index, 'Υπηρεσία Γαλλικά'] = edit_service_fr
                    df_c.at[index, 'Τιμή Συνάντησης'] = edit_price
                    df_c.to_csv(DB_CLIENTS, index=False)
                    st.session_state[f"edit_mode_{index}"] = False; st.rerun()

        st.markdown(f"## 📁 {client_name}")
        st.markdown(f"**Υπηρεσία:** {row['Υπηρεσία']}")
        st.divider()
        
        c_add, c_group = st.columns(2)
        if c_add.button("➕ Προσθήκη Μαθητή στο Club", use_container_width=True):
            add_student_to_club_dialog(client_name, row['Υπηρεσία'], row.get('Υπηρεσία Γαλλικά', ''), row.get('Τιμή Συνάντησης', 30.0))
        
        if c_group.button("📝 Ομαδική Καταχώρηση Συνεδρίας", type="primary", use_container_width=True):
            st.session_state[f"group_session_mode_{index}"] = not st.session_state[f"group_session_mode_{index}"]
            
        if st.session_state[f"group_session_mode_{index}"]:
            df_kids = df_c[(df_c["Φάκελος"] == client_name) & (df_c["Κατάσταση Πελάτη"] == "Ενεργός")].copy()
            if df_kids.empty:
                st.warning("Δεν υπάρχουν ενεργοί μαθητές σε αυτόν τον φάκελο.")
            else:
                with st.container(border=True):
                    st.subheader("Μαζική Καταχώρηση Παρουσιών")
                    date_input = st.date_input("Ημερομηνία", date.today())
                    duration = st.selectbox("Διάρκεια", ["1 ώρα", "1:30", "2 ώρες", "2:30"])
                    status = st.selectbox("Κατάσταση", ["Ολοκληρώθηκε", "Ακυρώθηκε Έγκαιρα (50%)", "Ακυρώθηκε Οριακά (100%)"])
                    
                    st.write("---")
                    st.write("Επιλέξτε ποιοι μαθητές **θα χρεωθούν** για αυτή τη συνεδρία:")
                    
                    df_kids.insert(0, "Επιλογή", True)
                    df_kids["Τιμή (CHF)"] = df_kids["Τιμή Συνάντησης"].apply(format_money)
                    
                    edited_kids = st.data_editor(
                        df_kids[["Επιλογή", "Όνομα Εφαρμογής", "Τιμή (CHF)"]], 
                        hide_index=True, use_container_width=True,
                        column_config={"Επιλογή": st.column_config.CheckboxColumn("Επιλογή", default=True)},
                        disabled=["Όνομα Εφαρμογής", "Τιμή (CHF)"]
                    )
                    
                    if st.button("💾 Αποθήκευση για τους Επιλεγμένους", type="primary", use_container_width=True):
                        selected_kids = edited_kids[edited_kids["Επιλογή"] == True]["Όνομα Εφαρμογής"].tolist()
                        if not selected_kids:
                            st.warning("Δεν επιλέξατε κανέναν μαθητή.")
                        else:
                            df_s = load_sessions()
                            new_sessions = []
                            df_c_upd = load_clients()
                            
                            multiplier = {"1 ώρα": 1.0, "1:30": 1.5, "2 ώρες": 2.0, "2:30": 2.5}[duration]
                            
                            for kid_app_name in selected_kids:
                                kid_idx = df_c_upd.index[df_c_upd['Όνομα Εφαρμογής'] == kid_app_name].tolist()[0]
                                base_amt = float(df_c_upd.at[kid_idx, 'Τιμή Συνάντησης'])
                                final_amt = base_amt * multiplier
                                if status == "Ακυρώθηκε Έγκαιρα (50%)": final_amt *= 0.5
                                
                                new_sessions.append({
                                    "Πελάτης": kid_app_name, "Ημερομηνία": date_input.strftime("%d/%m/%Y"), 
                                    "Κατάσταση Ραντεβού": status, "Ποσό": final_amt, 
                                    "Κατάσταση Πληρωμής": "🔴 Εκκρεμεί", "ID Απόδειξης": ""
                                })
                                df_c_upd.at[kid_idx, 'Συνολική Οφειλή'] = float(df_c_upd.at[kid_idx, 'Συνολική Οφειλή']) + float(final_amt)
                                
                            df_s = pd.concat([df_s, pd.DataFrame(new_sessions)], ignore_index=True)
                            df_s.to_csv(DB_SESSIONS, index=False)
                            df_c_upd.to_csv(DB_CLIENTS, index=False)
                            
                            st.success(f"Αποθηκεύτηκαν επιτυχώς οι συνεδρίες για {len(selected_kids)} μαθητές!")
                            st.session_state[f"group_session_mode_{index}"] = False
                            st.rerun()

        st.write("---")
        st.markdown("### 👥 Λίστα Μαθητών Φακέλου")
        df_kids_view = df_c[(df_c["Φάκελος"] == client_name) & (df_c["Κατάσταση Πελάτη"] == "Ενεργός")]
        if df_kids_view.empty: st.info("Δεν υπάρχουν ενεργοί μαθητές.")
        else:
            for k_idx, k_row in df_kids_view.iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{k_row['Όνομα Εφαρμογής']}** (Γονέας/Πελάτης: {k_row['Όνομα Γονέα 1']})")
                        st.caption(f"Τιμή: {format_money(k_row['Τιμή Συνάντησης'])} CHF | Οφειλή: :red[{format_money(k_row['Συνολική Οφειλή'])} CHF]")
                    with col2:
                        if st.button("Άνοιγμα", key=f"open_k_{k_idx}"):
                            st.session_state.selected_client_index = k_idx
                            st.rerun()
                            
    else: # ================== ΑΤΟΜΙΚΟ ΠΡΟΦΙΛ (ΚΑΝΟΝΙΚΟΣ Ή ΜΑΘΗΤΗΣ) ==================
        if t_btn2.button("✏️ Επεξεργασία", use_container_width=True):
            st.session_state[f"edit_mode_{index}"] = not st.session_state[f"edit_mode_{index}"]
            st.session_state[f"show_session_form_{index}"] = False; st.session_state[f"del_sess_mode_{index}"] = False; st.session_state[f"confirm_del_client_{index}"] = False; st.rerun()
        if t_btn3.button("🔴 Απενεργοποίηση", use_container_width=True):
            st.session_state[f"confirm_del_client_{index}"] = not st.session_state[f"confirm_del_client_{index}"]
            st.session_state[f"edit_mode_{index}"] = False; st.session_state[f"show_session_form_{index}"] = False; st.session_state[f"del_sess_mode_{index}"] = False; st.rerun()

        if st.session_state[f"confirm_del_client_{index}"]:
            st.warning("⚠️ Θέλετε να κάνετε τον πελάτη 'Ανενεργό'; Θα κρυφτεί από τις λίστες, αλλά τα στατιστικά του θα διατηρηθούν.")
            conf1, conf2 = st.columns(2)
            if conf1.button("✅ Ναι, Απενεργοποίηση", type="primary", use_container_width=True):
                df_c.at[index, 'Κατάσταση Πελάτη'] = "Αρχειοθετημένος"
                df_c.to_csv(DB_CLIENTS, index=False)
                st.session_state.current_page = "clients_list"; st.rerun()
            if conf2.button("❌ Ακύρωση", use_container_width=True): st.session_state[f"confirm_del_client_{index}"] = False; st.rerun()

        if st.session_state[f"edit_mode_{index}"]:
            with st.container(border=True):
                e1, e2 = st.columns(2)
                with e1:
                    edit_app_name = st.text_input("Όνομα στην Εφαρμογή", value=row['Όνομα Εφαρμογής'])
                    edit_child = st.text_input("Όνομα Παιδιού / Μαθητή", value=row.get('Όνομα Παιδιού', ''))
                    edit_parent1 = st.text_input("Όνομα Πελάτη / Γονέα 1 *", value=row.get('Όνομα Γονέα 1', ''))
                    edit_parent2 = st.text_input("Όνομα Γονέα 2", value=row.get('Όνομα Γονέα 2', ''))
                    edit_address = st.text_input("Πλήρης Διεύθυνση", value=row.get('Διεύθυνση', ''))
                with e2:
                    edit_service_txt = st.text_input("Υπηρεσία", value=row['Υπηρεσία'])
                    edit_service_fr = st.text_input("Υπηρεσία Γαλλικά", value=row.get('Υπηρεσία Γαλλικά', ''))
                    edit_tel1 = st.text_input("Τηλέφωνο 1", value=row.get('Τηλέφωνο 1', ''))
                    edit_tel2 = st.text_input("Τηλέφωνο 2", value=row.get('Τηλέφωνο 2', ''))
                    edit_email1 = st.text_input("Email 1", value=row.get('Email 1', ''))
                    
                price_str = st.text_input("Τιμή Συνάντησης (CHF)", value=str(row['Τιμή Συνάντησης']))
                try: edit_price = float(price_str.replace(",", "."))
                except ValueError: edit_price = float(row['Τιμή Συνάντησης'])
                edit_debt = st.number_input("Συνολική Οφειλή", value=float(row['Συνολική Οφειλή']), step=5.0)
                edit_notes = st.text_area("Σημειώσεις", value=row.get('Σημειώσεις', ''))
                    
                if st.button("💾 Αποθήκευση", type="primary", use_container_width=True):
                    df_c.at[index, 'Όνομα Εφαρμογής'] = edit_app_name
                    df_c.at[index, 'Όνομα Παιδιού'] = edit_child; df_c.at[index, 'Όνομα Γονέα 1'] = edit_parent1; df_c.at[index, 'Όνομα Γονέα 2'] = edit_parent2
                    df_c.at[index, 'Διεύθυνση'] = edit_address
                    df_c.at[index, 'Τηλέφωνο 1'] = edit_tel1; df_c.at[index, 'Τηλέφωνο 2'] = edit_tel2; df_c.at[index, 'Email 1'] = edit_email1
                    df_c.at[index, 'Υπηρεσία'] = edit_service_txt; df_c.at[index, 'Υπηρεσία Γαλλικά'] = edit_service_fr
                    df_c.at[index, 'Σημειώσεις'] = edit_notes
                    df_c.at[index, 'Τιμή Συνάντησης'] = edit_price; df_c.at[index, 'Συνολική Οφειλή'] = edit_debt
                    df_c.to_csv(DB_CLIENTS, index=False)
                    if edit_app_name != client_name:
                        df_s = load_sessions(); df_s.loc[df_s["Πελάτης"] == client_name, "Πελάτης"] = edit_app_name; df_s.to_csv(DB_SESSIONS, index=False)
                    st.session_state[f"edit_mode_{index}"] = False; st.rerun()

        prefix = "🎓" if client_type == "Μαθητής" else "👤"
        st.markdown(f"## {prefix} {client_name}")
        if row.get('Φάκελος', ''): st.caption(f"Φάκελος / Club: **{row['Φάκελος']}**")
        st.markdown(f"**Υπηρεσία:** {row['Υπηρεσία']}")
        
        info1, info2 = st.columns(2)
        info1.markdown(f"**Πελάτης / Γονέας 1:** {row.get('Όνομα Γονέα 1', '-')}")
        if str(row.get('Όνομα Γονέα 2', '')).strip(): info1.markdown(f"**Γονέας 2:** {row['Όνομα Γονέα 2']}")
        info1.markdown(f"**Διεύθυνση:** {row.get('Διεύθυνση', '-')}")
        
        contact_str = ""
        if str(row.get('Τηλέφωνο 1', '')).strip(): contact_str += f"📞 {row['Τηλέφωνο 1']}<br>"
        if str(row.get('Email 1', '')).strip(): contact_str += f"✉️ {row['Email 1']}<br>"
        if str(row.get('Τηλέφωνο 2', '')).strip(): contact_str += f"📞 {row['Τηλέφωνο 2']} (Γ2)"
        
        info2.markdown(f"**Επικοινωνία:**<br>{contact_str}", unsafe_allow_html=True)
        
        st.write("---")
        info3, info4 = st.columns(2)
        info3.markdown(f"**Αρχικό Ποσό Συνεδρίας:** {format_money(row['Τιμή Συνάντησης'])} CHF")
        info4.markdown(f"**Τρέχουσα Οφειλή:** :red[{format_money(row['Συνολική Οφειλή'])} CHF]")
        
        notes_val = row.get('Σημειώσεις', '')
        if str(notes_val).strip():
            st.markdown(f"**Σημειώσεις:**\n{notes_val}")
            
        st.divider()
        
        c_btn1, c_btn2 = st.columns(2)
        if c_btn1.button("📝 Νέα Συνεδρία (Ατομική)", type="primary", use_container_width=True):
            st.session_state[f"show_session_form_{index}"] = not st.session_state[f"show_session_form_{index}"]
            st.session_state[f"del_sess_mode_{index}"] = False; st.session_state[f"edit_mode_{index}"] = False; st.session_state[f"confirm_del_client_{index}"] = False; st.rerun()
        if c_btn2.button("✏️ Επεξεργασία Συνεδριών", use_container_width=True):
            st.session_state[f"del_sess_mode_{index}"] = not st.session_state[f"del_sess_mode_{index}"]
            st.session_state[f"show_session_form_{index}"] = False; st.session_state[f"edit_mode_{index}"] = False; st.session_state[f"confirm_del_client_{index}"] = False; st.rerun()

        if st.session_state[f"show_session_form_{index}"]:
            with st.container(border=True):
                form_c1, form_c2 = st.columns(2)
                with form_c1:
                    date_input = st.date_input("Ημερομηνία", date.today())
                    duration = st.selectbox("Διάρκεια", ["1 ώρα", "1:30", "2 ώρες", "2:30"])
                    status = st.selectbox("Κατάσταση", ["Ολοκληρώθηκε", "Ακυρώθηκε Έγκαιρα (50%)", "Ακυρώθηκε Οριακά (100%)"])
                with form_c2:
                    base_amt = st.number_input("Αρχικό Ποσό", value=float(row['Τιμή Συνάντησης']), step=5.0)
                    payment_base = st.selectbox("Πληρωμή", ["🔴 Εκκρεμεί", "🟢 Εξοφλήθηκε"], index=0)
                    
                with st.container(border=True):
                    st.markdown("<h6 style='color: #ff9800; margin-bottom: 5px;'>🟠 Promo / Pro Bono</h6>", unsafe_allow_html=True)
                    is_gift = st.checkbox("Καταχώρηση ως δωρεάν παροχή (δεν τιμολογείται)")
                    
                if is_gift:
                    if "Εκκρεμεί" in payment_base: payment = "🟠 Εκκρεμεί (Promo / Pro Bono)"
                    else: payment = "🟣 Ολοκληρώθηκε (Promo / Pro Bono)"
                else:
                    payment = payment_base
                    
                multiplier = {"1 ώρα": 1.0, "1:30": 1.5, "2 ώρες": 2.0, "2:30": 2.5}[duration]
                final_amt = base_amt * multiplier
                if status == "Ακυρώθηκε Έγκαιρα (50%)": final_amt = final_amt * 0.5
                st.info(f"💰 **Τελικό Ποσό:** {format_money(final_amt)} CHF")

                def save_session_logic(update_base_price=False):
                    new_session = pd.DataFrame([{"Πελάτης": client_name, "Ημερομηνία": date_input.strftime("%d/%m/%Y"), "Κατάσταση Ραντεβού": status, "Ποσό": final_amt, "Κατάσταση Πληρωμής": payment, "ID Απόδειξης": ""}])
                    df_s = load_sessions()
                    df_s = pd.concat([df_s, new_session], ignore_index=True)
                    df_s.to_csv(DB_SESSIONS, index=False)
                    df_c_reload = load_clients()
                    
                    if "🔴 Εκκρεμεί" == payment or "🟠 Εκκρεμεί" in payment:
                        df_c_reload.at[index, 'Συνολική Οφειλή'] = float(df_c_reload.at[index, 'Συνολική Οφειλή']) + float(final_amt)
                    if update_base_price: df_c_reload.at[index, 'Τιμή Συνάντησης'] = float(base_amt)
                    df_c_reload.to_csv(DB_CLIENTS, index=False)
                    st.session_state[f"show_session_form_{index}"] = False; st.rerun()

                if base_amt != float(row['Τιμή Συνάντησης']):
                    st.warning("⚠️ Αλλάξατε το Αρχικό Ποσό. Πώς θέλετε να το αποθηκεύσετε;")
                    btn_save1, btn_save2 = st.columns(2)
                    if btn_save1.button("Αποθήκευση & Μόνιμη Ενημέρωση Πελάτη", use_container_width=True): save_session_logic(True)
                    if btn_save2.button("Μόνο για αυτή τη φορά", type="primary", use_container_width=True): save_session_logic(False)
                else:
                    if st.button("💾 Αποθήκευση Συνεδρίας", type="primary", use_container_width=True): save_session_logic(False)

        st.write("---")
        st.markdown("### 📊 Ιστορικό Συνεδριών (Ατομικό)")
        df_s = load_sessions()
        client_sessions = df_s[df_s["Πελάτης"] == client_name].copy()
        if client_sessions.empty: st.info("Δεν έχουν καταχωρηθεί συνεδρίες.")
        else:
            client_sessions['orig_id'] = client_sessions.index
            client_sessions['sort_date'] = pd.to_datetime(client_sessions['Ημερομηνία'], format="%d/%m/%Y", errors='coerce')
            client_sessions = client_sessions.sort_values(by=['sort_date', 'orig_id'], ascending=[False, False]).drop(columns=['sort_date', 'orig_id'])

            if st.session_state[f"del_sess_mode_{index}"]:
                display_df = client_sessions[client_sessions["Κατάσταση Πληρωμής"] != "🟢 Εξοφλήθηκε"].drop(columns=["Πελάτης", "ID Απόδειξης", "Κατάσταση Ραντεβού"], errors='ignore')
                
                if display_df.empty:
                    st.info("Δεν υπάρχ διαθέσιμες συνεδρίες για αλλαγή (οι επίσημα εξοφλημένες δεν μπορούν να τροποποιηθούν).")
                    if st.button("Κλείσιμο", use_container_width=True):
                        st.session_state[f"del_sess_mode_{index}"] = False; st.rerun()
                else:
                    display_df.insert(0, "Επιλογή", False)
                    display_df["Ποσό"] = display_df["Ποσό"].apply(format_money)
                    edited_df = st.data_editor(display_df, hide_index=True, use_container_width=True, column_config={"Επιλογή": st.column_config.CheckboxColumn("Επιλογή", default=False)}, disabled=["Ημερομηνία", "Ποσό", "Κατάσταση Πληρωμής"])
                    selected_indices = edited_df[edited_df["Επιλογή"] == True].index.tolist()
                    
                    if len(selected_indices) > 0:
                        c_red, c_org, c_pur, c_del = st.columns(4)
                        
                        if c_red.button("🔴 Αλλαγή σε Εκκρεμεί", use_container_width=True):
                            df_s_upd = load_sessions(); df_c_upd = load_clients()
                            for idx_s in selected_indices:
                                status_val = str(df_s_upd.at[idx_s, "Κατάσταση Πληρωμής"])
                                if status_val != "🔴 Εκκρεμεί":
                                    amt = float(df_s_upd.at[idx_s, "Ποσό"])
                                    df_c_upd.at[index, 'Συνολική Οφειλή'] = float(df_c_upd.at[index, 'Συνολική Οφειλή']) + amt
                                df_s_upd.at[idx_s, "Κατάσταση Πληρωμής"] = "🔴 Εκκρεμεί"
                            df_s_upd.to_csv(DB_SESSIONS, index=False); df_c_upd.to_csv(DB_CLIENTS, index=False)
                            st.session_state[f"action_done_{index}"] = True; st.rerun()
                            
                        if c_org.button("🟠 Αλλαγή σε Εκκρεμεί (Promo)", use_container_width=True):
                            df_s_upd = load_sessions(); df_c_upd = load_clients()
                            for idx_s in selected_indices:
                                status_val = str(df_s_upd.at[idx_s, "Κατάσταση Πληρωμής"])
                                if status_val == "🔴 Εκκρεμεί":
                                    amt = float(df_s_upd.at[idx_s, "Ποσό"]); df_c_upd.at[index, 'Συνολική Οφειλή'] = max(0.0, float(df_c_upd.at[index, 'Συνολική Οφειλή']) - amt)
                                df_s_upd.at[idx_s, "Κατάσταση Πληρωμής"] = "🟠 Εκκρεμεί (Promo / Pro Bono)"
                            df_s_upd.to_csv(DB_SESSIONS, index=False); df_c_upd.to_csv(DB_CLIENTS, index=False)
                            st.session_state[f"action_done_{index}"] = True; st.rerun()
                            
                        if c_pur.button("🟣 Αλλαγή σε Ολοκληρώθηκε (Promo)", use_container_width=True):
                            df_s_upd = load_sessions(); df_c_upd = load_clients()
                            for idx_s in selected_indices:
                                status_val = str(df_s_upd.at[idx_s, "Κατάσταση Πληρωμής"])
                                if status_val == "🔴 Εκκρεμεί":
                                    amt = float(df_s_upd.at[idx_s, "Ποσό"]); df_c_upd.at[index, 'Συνολική Οφειλή'] = max(0.0, float(df_c_upd.at[index, 'Συνολική Οφειλή']) - amt)
                                df_s_upd.at[idx_s, "Κατάσταση Πληρωμής"] = "🟣 Ολοκληρώθηκε (Promo / Pro Bono)"
                            df_s_upd.to_csv(DB_SESSIONS, index=False); df_c_upd.to_csv(DB_CLIENTS, index=False)
                            st.session_state[f"action_done_{index}"] = True; st.rerun()

                        if c_del.button("🗑️ Διαγραφή", use_container_width=True):
                            df_s_upd = load_sessions(); df_c_upd = load_clients()
                            for idx_s in selected_indices:
                                status_val = str(df_s_upd.at[idx_s, "Κατάσταση Πληρωμής"])
                                if status_val == "🔴 Εκκρεμεί":
                                    amt = float(df_s_upd.at[idx_s, "Ποσό"]); df_c_upd.at[index, 'Συνολική Οφειλή'] = max(0.0, float(df_c_upd.at[index, 'Συνολική Οφειλή']) - amt)
                                df_s_upd = df_s_upd.drop(idx_s)
                            df_s_upd.to_csv(DB_SESSIONS, index=False); df_c_upd.to_csv(DB_CLIENTS, index=False)
                            st.session_state[f"action_done_{index}"] = True; st.rerun()
                    
                    if st.session_state.get(f"action_done_{index}", False):
                        st.success("✅ Η αλλαγή πραγματοποιήθηκε με επιτυχία!")
                        if st.button("Έχετε ολοκληρώσει την αλλαγή; (Ναι)", type="primary"):
                            st.session_state[f"action_done_{index}"] = False
                            st.rerun()
            else:
                view_mode = st.radio("Προβολή:", ["📅 Ενιαία Λίστα", "🗂️ Διαχωρισμός"], horizontal=True, key=f"v_mode_{index}")
                c_disp = client_sessions.drop(columns=["Πελάτης", "ID Απόδειξης"], errors='ignore')
                if view_mode == "📅 Ενιαία Λίστα": st.dataframe(apply_color_status(c_disp), hide_index=True, use_container_width=True)
                else:
                    df_pend = c_disp[c_disp["Κατάσταση Πληρωμής"].str.contains("Εκκρεμεί")]
                    df_paid = c_disp[c_disp["Κατάσταση Πληρωμής"].str.contains("Εξοφλήθηκε|Ολοκληρώθηκε")]
                    st.markdown("🔴 **Εκκρεμούν**")
                    if df_pend.empty: st.info("Καμία εκκρεμότητα.")
                    else: st.dataframe(apply_color_status(df_pend), hide_index=True, use_container_width=True)
                    st.markdown("🟢 **Εξοφλήθηκαν / Promo**")
                    if df_paid.empty: st.info("Καμία εξοφλημένη συνεδρία.")
                    else: st.dataframe(apply_color_status(df_paid), hide_index=True, use_container_width=True)

# ==========================================
# ΣΕΛΙΔΑ 4: ΟΛΕΣ ΟΙ ΣΥΝΕΔΡΙΕΣ (ΜΕ ΜΑΖΙΚΗ ΕΠΕΞΕΡΓΑΣΙΑ)
# ==========================================
def show_all_sessions_page():
    st.title("📅 Ιστορικό Συνεδριών")
    if st.button("🔙 Επιστροφή στο Κεντρικό Μενού", use_container_width=True): st.session_state.current_page = "home"; st.rerun()
    df_s = load_sessions()
    if df_s.empty: st.info("Δεν έχουν καταχωρηθεί συνεδρίες ακόμα."); return
    
    df_merged = df_s.copy()
    df_merged['sort_date'] = pd.to_datetime(df_merged['Ημερομηνία'], format="%d/%m/%Y", errors='coerce')
    all_years = sorted(df_merged['sort_date'].dt.year.dropna().astype(int).astype(str).unique().tolist(), reverse=True) if not df_merged.empty else []
    
    st.write("---")
    st.markdown("### 🔍 Φίλτρα & Αναζήτηση")
    c1, c3, c4 = st.columns(3)
    with c1: sel_app = st.selectbox("Πελάτης / Μαθητής", ["Όλοι"] + df_merged["Πελάτης"].dropna().unique().tolist())
    with c3: sel_year = st.selectbox("Έτος", ["Όλα"] + all_years)
    with c4: sel_month = st.selectbox("Μήνας", MONTHS_LIST)

    if sel_app != "Όλοι": df_merged = df_merged[df_merged["Πελάτης"] == sel_app]
    if sel_year != "Όλα": df_merged = df_merged[df_merged['sort_date'].dt.year.fillna(0).astype(int).astype(str) == sel_year]
    if sel_month != "Όλοι": 
        m_num = int(sel_month.split(" - ")[0])
        df_merged = df_merged[df_merged['sort_date'].dt.month == m_num]
        
    df_merged['orig_id'] = df_merged.index
    df_merged = df_merged.sort_values(by=['sort_date', 'orig_id'], ascending=[False, False]).drop(columns=['sort_date'])

    st.write("---")
    
    edit_mode_all = st.toggle("✏️ Επεξεργασία Συνεδριών", key="toggle_edit_all")
    
    if edit_mode_all:
        display_df = df_merged[df_merged["Κατάσταση Πληρωμής"] != "🟢 Εξοφλήθηκε"].copy()
        
        if display_df.empty:
            st.info("Δεν υπάρχουν διαθέσιμες συνεδρίες για αλλαγή (οι επίσημα εξοφλημένες δεν μπορούν να τροποποιηθούν).")
        else:
            display_df.insert(0, "Επιλογή", False)
            display_df["Ποσό"] = display_df["Ποσό"].apply(format_money)
            
            edited_df = st.data_editor(
                display_df.drop(columns=["orig_id", "ID Απόδειξης", "Κατάσταση Ραντεβού"], errors='ignore'), 
                hide_index=True, 
                use_container_width=True, 
                column_config={"Επιλογή": st.column_config.CheckboxColumn("Επιλογή", default=False)}, 
                disabled=["Πελάτης", "Ημερομηνία", "Ποσό", "Κατάσταση Πληρωμής"]
            )
            
            selected_rows_bool = edited_df["Επιλογή"] == True
            selected_indices = display_df[selected_rows_bool]["orig_id"].tolist()
            
            if len(selected_indices) > 0:
                c_red, c_org, c_pur, c_del = st.columns(4)

                if c_red.button("🔴 Αλλαγή σε Εκκρεμεί", use_container_width=True):
                    df_s_upd = load_sessions(); df_c_upd = load_clients()
                    for idx_s in selected_indices:
                        status_val = str(df_s_upd.at[idx_s, "Κατάσταση Πληρωμής"])
                        if status_val != "🔴 Εκκρεμεί":
                            amt = float(df_s_upd.at[idx_s, "Ποσό"]); app_name = df_s_upd.at[idx_s, "Πελάτης"]
                            if app_name in df_c_upd["Όνομα Εφαρμογής"].values:
                                c_idx = df_c_upd.index[df_c_upd["Όνομα Εφαρμογής"] == app_name].tolist()[0]
                                df_c_upd.at[c_idx, 'Συνολική Οφειλή'] = float(df_c_upd.at[c_idx, 'Συνολική Οφειλή']) + amt
                        df_s_upd.at[idx_s, "Κατάσταση Πληρωμής"] = "🔴 Εκκρεμεί"
                    df_s_upd.to_csv(DB_SESSIONS, index=False); df_c_upd.to_csv(DB_CLIENTS, index=False)
                    st.session_state["action_done_all"] = True; st.rerun()

                if c_org.button("🟠 Αλλαγή σε Εκκρεμεί (Promo)", use_container_width=True):
                    df_s_upd = load_sessions(); df_c_upd = load_clients()
                    for idx_s in selected_indices:
                        status_val = str(df_s_upd.at[idx_s, "Κατάσταση Πληρωμής"])
                        if status_val == "🔴 Εκκρεμεί":
                            amt = float(df_s_upd.at[idx_s, "Ποσό"]); app_name = df_s_upd.at[idx_s, "Πελάτης"]
                            if app_name in df_c_upd["Όνομα Εφαρμογής"].values:
                                c_idx = df_c_upd.index[df_c_upd["Όνομα Εφαρμογής"] == app_name].tolist()[0]
                                df_c_upd.at[c_idx, 'Συνολική Οφειλή'] = max(0.0, float(df_c_upd.at[c_idx, 'Συνολική Οφειλή']) - amt)
                        df_s_upd.at[idx_s, "Κατάσταση Πληρωμής"] = "🟠 Εκκρεμεί (Promo / Pro Bono)"
                    df_s_upd.to_csv(DB_SESSIONS, index=False); df_c_upd.to_csv(DB_CLIENTS, index=False)
                    st.session_state["action_done_all"] = True; st.rerun()

                if c_pur.button("🟣 Αλλαγή σε Ολοκληρώθηκε (Promo)", use_container_width=True):
                    df_s_upd = load_sessions(); df_c_upd = load_clients()
                    for idx_s in selected_indices:
                        status_val = str(df_s_upd.at[idx_s, "Κατάσταση Πληρωμής"])
                        if status_val == "🔴 Εκκρεμεί":
                            amt = float(df_s_upd.at[idx_s, "Ποσό"]); app_name = df_s_upd.at[idx_s, "Πελάτης"]
                            if app_name in df_c_upd["Όνομα Εφαρμογής"].values:
                                c_idx = df_c_upd.index[df_c_upd["Όνομα Εφαρμογής"] == app_name].tolist()[0]
                                df_c_upd.at[c_idx, 'Συνολική Οφειλή'] = max(0.0, float(df_c_upd.at[c_idx, 'Συνολική Οφειλή']) - amt)
                        df_s_upd.at[idx_s, "Κατάσταση Πληρωμής"] = "🟣 Ολοκληρώθηκε (Promo / Pro Bono)"
                    df_s_upd.to_csv(DB_SESSIONS, index=False); df_c_upd.to_csv(DB_CLIENTS, index=False)
                    st.session_state["action_done_all"] = True; st.rerun()

                if c_del.button("🗑️ Διαγραφή", use_container_width=True):
                    df_s_upd = load_sessions(); df_c_upd = load_clients()
                    for idx_s in selected_indices:
                        status_val = str(df_s_upd.at[idx_s, "Κατάσταση Πληρωμής"])
                        if status_val == "🔴 Εκκρεμεί":
                            amt = float(df_s_upd.at[idx_s, "Ποσό"]); app_name = df_s_upd.at[idx_s, "Πελάτης"]
                            if app_name in df_c_upd["Όνομα Εφαρμογής"].values:
                                c_idx = df_c_upd.index[df_c_upd["Όνομα Εφαρμογής"] == app_name].tolist()[0]
                                df_c_upd.at[c_idx, 'Συνολική Οφειλή'] = max(0.0, float(df_c_upd.at[c_idx, 'Συνολική Οφειλή']) - amt)
                        df_s_upd = df_s_upd.drop(idx_s)
                    df_s_upd.to_csv(DB_SESSIONS, index=False); df_c_upd.to_csv(DB_CLIENTS, index=False)
                    st.session_state["action_done_all"] = True; st.rerun()
            
            if st.session_state.get("action_done_all", False):
                st.success("✅ Η αλλαγή πραγματοποιήθηκε με επιτυχία!")
                if st.button("Έχετε ολοκληρώσει την αλλαγή; (Ναι)", type="primary"):
                    st.session_state["action_done_all"] = False
                    st.rerun()
    else:
        view_opt = st.radio("Τρόπος Προβολής:", ["📅 Ενιαία Λίστα", "🗂️ Διαχωρισμός"], horizontal=True)
        display_merged = df_merged.drop(columns=["orig_id", "ID Απόδειξης"], errors='ignore')
        if view_opt == "📅 Ενιαία Λίστα": st.dataframe(apply_color_status(display_merged), hide_index=True, use_container_width=True)
        else:
            df_pend = display_merged[display_merged["Κατάσταση Πληρωμής"].str.contains("Εκκρεμεί")]
            df_paid = display_merged[display_merged["Κατάσταση Πληρωμής"].str.contains("Εξοφλήθηκε|Ολοκληρώθηκε")]
            st.markdown("🔴 **Εκκρεμούν**")
            if df_pend.empty: st.info("Καμία εκκρεμότητα.")
            else: st.dataframe(apply_color_status(df_pend), hide_index=True, use_container_width=True)
            st.markdown("🟢 **Εξοφλήθηκαν / Promo**")
            if df_paid.empty: st.info("Καμία εξοφλημένη συνεδρία.")
            else: st.dataframe(apply_color_status(df_paid), hide_index=True, use_container_width=True)

def show_expenses_page():
    st.title("📉 Έξοδα")
    if st.button("🔙 Επιστροφή στο Κεντρικό Μενού", use_container_width=True): st.session_state.current_page = "home"; st.rerun()
    df_e = load_expenses()
    if df_e.empty: st.info("Δεν έχουν καταχωρηθεί έξοδα ακόμα.")
    else:
        st.write("---")
        st.markdown("### 🔍 Φίλτρα Αναζήτησης")
        df_e['sort_date'] = pd.to_datetime(df_e['Ημερομηνία'], format="%d/%m/%Y", errors='coerce')
        all_years = sorted(df_e['sort_date'].dt.year.dropna().astype(int).astype(str).unique().tolist(), reverse=True) if not df_e.empty else []
        
        c1, c2 = st.columns(2)
        with c1: sel_year = st.selectbox("Έτος", ["Όλα"] + all_years)
        with c2: sel_month = st.selectbox("Μήνας", MONTHS_LIST)
        
        if sel_year != "Όλα": df_e = df_e[df_e['sort_date'].dt.year.fillna(0).astype(int).astype(str) == sel_year]
        if sel_month != "Όλοι": 
            m_num = int(sel_month.split(" - ")[0])
            df_e = df_e[df_e['sort_date'].dt.month == m_num]
            
        total_expenses = df_e["Ποσό (CHF)"].astype(float).sum()
        st.metric(label="Συνολικά Έξοδα (Επιλεγμένης Περιόδου)", value=f"{format_money(total_expenses)} CHF")
        
        df_e['orig_id'] = df_e.index
        df_e = df_e.sort_values(by=['sort_date', 'orig_id'], ascending=[False, False]).drop(columns=['sort_date'])
        
        edit_mode_exp = st.toggle("✏️ Επεξεργασία / Διαγραφή Εξόδων")
        
        if edit_mode_exp:
            display_e = df_e.copy()
            display_e.insert(0, "Επιλογή", False)
            display_e["Ποσό (CHF)"] = display_e["Ποσό (CHF)"].apply(format_money)
            
            ed_e = st.data_editor(
                display_e.drop(columns=["orig_id", "Αρχείο Απόδειξης"], errors='ignore'), 
                hide_index=True, 
                use_container_width=True,
                column_config={"Επιλογή": st.column_config.CheckboxColumn("Επιλογή", default=False)},
                disabled=["Ημερομηνία", "Είδος Εξόδου", "Ποσό (CHF)", "Σημειώσεις"]
            )
            
            selected_e = ed_e[ed_e["Επιλογή"] == True].index.tolist()
            if len(selected_e) > 0:
                if st.button("🗑️ Διαγραφή Επιλεγμένων", type="primary", use_container_width=True):
                    real_indices = display_e.iloc[selected_e]["orig_id"].tolist()
                    df_e_upd = load_expenses()
                    for idx_e in real_indices:
                        file_n = df_e_upd.at[idx_e, "Αρχείο Απόδειξης"]
                        if file_n != "-" and pd.notna(file_n):
                            f_path = os.path.join(UPLOAD_DIR, file_n)
                            if os.path.exists(f_path): os.remove(f_path)
                    df_e_upd = df_e_upd.drop(real_indices)
                    df_e_upd.to_csv(DB_EXPENSES, index=False)
                    st.rerun()
        else:
            st.dataframe(df_e.drop(columns=["orig_id", "Αρχείο Απόδειξης"], errors='ignore').style.format({'Ποσό (CHF)': format_money}), hide_index=True, use_container_width=True)
            
            df_files = df_e[df_e["Αρχείο Απόδειξης"] != "-"]
            if not df_files.empty:
                st.markdown("#### 📎 Προβολή Αποδεικτικών")
                for idx, row in df_files.iterrows():
                    if st.button(f"👁️ {row['Είδος Εξόδου']} - {row['Ημερομηνία']} ({format_money(row['Ποσό (CHF)'])} CHF)", key=f"view_exp_{row['orig_id']}", use_container_width=True):
                        view_receipt_dialog(os.path.join(UPLOAD_DIR, row["Αρχείο Απόδειξης"]))

def show_statistics_page():
    st.title("📊 Στατιστικά & Οικονομικά")
    if st.button("🔙 Επιστροφή στο Κεντρικό Μενού", use_container_width=True): st.session_state.current_page = "home"; st.rerun()
    df_s = load_sessions(); df_e = load_expenses(); df_c = load_clients()
    
    st.markdown("### 🔍 Φίλτρα Περιόδου")
    df_s['sort_date'] = pd.to_datetime(df_s['Ημερομηνία'], format="%d/%m/%Y", errors='coerce') if not df_s.empty else pd.Series()
    df_e['sort_date'] = pd.to_datetime(df_e['Ημερομηνία'], format="%d/%m/%Y", errors='coerce') if not df_e.empty else pd.Series()
    
    y_s = df_s['sort_date'].dt.year.dropna().astype(int).astype(str).unique().tolist() if not df_s.empty else []
    y_e = df_e['sort_date'].dt.year.dropna().astype(int).astype(str).unique().tolist() if not df_e.empty else []
    all_years = sorted(list(set(y_s + y_e)), reverse=True)
    
    c1, c2 = st.columns(2)
    with c1: sel_year = st.selectbox("Έτος", ["Όλα"] + all_years)
    with c2: sel_month = st.selectbox("Μήνας", MONTHS_LIST)
    
    if sel_year != "Όλα":
        if not df_s.empty: df_s = df_s[df_s['sort_date'].dt.year.fillna(0).astype(int).astype(str) == sel_year]
        if not df_e.empty: df_e = df_e[df_e['sort_date'].dt.year.fillna(0).astype(int).astype(str) == sel_year]
    if sel_month != "Όλοι":
        m_num = int(sel_month.split(" - ")[0])
        if not df_s.empty: df_s = df_s[df_s['sort_date'].dt.month == m_num]
        if not df_e.empty: df_e = df_e[df_e['sort_date'].dt.month == m_num]
        
    total_income = paid_income = pending_income = gift_value = 0.0
    if not df_s.empty:
        df_s["Ποσό"] = df_s["Ποσό"].astype(float)
        paid_income = df_s[df_s["Κατάσταση Πληρωμής"] == "🟢 Εξοφλήθηκε"]["Ποσό"].sum()
        pending_income = df_s[df_s["Κατάσταση Πληρωμής"] == "🔴 Εκκρεμεί"]["Ποσό"].sum()
        gift_value = df_s[df_s["Κατάσταση Πληρωμής"].str.contains("Promo", regex=True)]["Ποσό"].sum()
        total_income = paid_income + pending_income
        
    total_expenses = 0.0
    if not df_e.empty:
        df_e["Ποσό (CHF)"] = df_e["Ποσό (CHF)"].astype(float)
        total_expenses = df_e["Ποσό (CHF)"].sum()
        
    st.write("---")
    st.subheader("Συνολική Εικόνα (Επιλεγμένης Περιόδου)")
    m1, m2, m3 = st.columns(3)
    m1.metric("Συνολικά Έσοδα", f"{format_money(total_income)} CHF")
    m2.metric("Εξοφλήθηκαν", f"{format_money(paid_income)} CHF")
    m3.metric("Εκκρεμούν", f"{format_money(pending_income)} CHF")
    e1, e2, e3 = st.columns(3)
    e1.metric("Συνολικά Έξοδα", f"{format_money(total_expenses)} CHF")
    e2.metric("Καθαρό Κέρδος", f"{format_money(total_income - total_expenses)} CHF")
    e3.metric("💜 Αξία Δωρεάν Παροχών (Promo)", f"{format_money(gift_value)} CHF")
    
    # --- ΕΝΟΤΗΤΑ EXPORT ΓΙΑ ΛΟΓΙΣΤΗ ---
    st.write("---")
    st.subheader("💾 Εξαγωγή Δεδομένων για τον Λογιστή (Excel / CSV)")
    
    exp_lang = st.radio("Επιλογή Γλώσσας για το αρχείο:", ["Ελληνικά", "Français (Γαλλικά)"])
    
    if st.button("📥 Λήψη Εσόδων (Συνεδρίες)", use_container_width=True):
        df_export_s = load_sessions()
        if not df_export_s.empty:
            df_export_s = df_export_s[~df_export_s["Κατάσταση Πληρωμής"].str.contains("Promo", regex=True, na=False)].copy()
            
            if exp_lang == "Français (Γαλλικά)":
                df_export_s = df_export_s.rename(columns={
                    "Πελάτης": "Client", "Ημερομηνία": "Date", 
                    "Κατάσταση Ραντεβού": "Statut RDV", "Ποσό": "Montant (CHF)", 
                    "Κατάσταση Πληρωμής": "Statut de Paiement", "ID Απόδειξης": "ID Facture"
                })
                df_export_s["Statut de Paiement"] = df_export_s["Statut de Paiement"].str.replace("🔴 Εκκρεμεί", "En attente").str.replace("🟢 Εξοφλήθηκε", "Payé")
                df_export_s["Statut RDV"] = df_export_s["Statut RDV"].replace({"Ολοκληρώθηκε": "Terminé", "Ακυρώθηκε Έγκαιρα (50%)": "Annulé à l'avance (50%)", "Ακυρώθηκε Οριακά (100%)": "Annulé tardivement (100%)"})
            
            csv_data = df_export_s.to_csv(index=False, encoding='utf-8-sig') 
            st.download_button(label="Αποθήκευση CSV Εσόδων", data=csv_data, file_name="Revenus_Sessions.csv", mime="text/csv", type="primary")
        else:
            st.warning("Δεν υπάρχουν επίσημες συνεδρίες για εξαγωγή.")

    if st.button("📥 Λήψη Εξόδων", use_container_width=True):
        df_export_e = load_expenses()
        if not df_export_e.empty:
            df_export_e = df_export_e.drop(columns=["Αρχείο Απόδειξης"], errors='ignore')
            if exp_lang == "Français (Γαλλικά)":
                df_export_e = df_export_e.rename(columns={
                    "Ημερομηνία": "Date", "Είδος Εξόδου": "Type de dépense", 
                    "Ποσό (CHF)": "Montant (CHF)", "Σημειώσεις": "Notes"
                })
            csv_data = df_export_e.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(label="Αποθήκευση CSV Εξόδων", data=csv_data, file_name="Depenses.csv", mime="text/csv", type="primary")
        else:
            st.warning("Δεν υπάρχουν έξοδα για εξαγωγή.")

# --- ROUTING ΕΦΑΡΜΟΓΗΣ ---
if st.session_state.current_page == "home": show_home_page()
elif st.session_state.current_page == "clients_list": show_clients_list_page()
elif st.session_state.current_page == "client_profile": show_client_profile()
elif st.session_state.current_page == "all_sessions": show_all_sessions_page()
elif st.session_state.current_page == "expenses_list": show_expenses_page()
elif st.session_state.current_page == "statistics_page": show_statistics_page()
elif st.session_state.current_page == "invoices_page": show_invoices_page()
