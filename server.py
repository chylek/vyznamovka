import gensim
from pytz import UTC
import tornado.ioloop
import tornado.web
import datetime
import json
from threading import Lock

w2v_path = "cs_syn_vectors.bin"
kv = gensim.models.KeyedVectors.load_word2vec_format(w2v_path, binary=True)
secrets = ["knihovna", "noční", "patřit", "množství", "operace", "blízko", "právě", "píseň", "investice", "následovat", "hovořit", "skutečnost", "vnitřní", "rychle", "jestliže", "opět", "promluvit", "politik", "teorie", "spojit", "skvělý", "táta", "drahý", "navrhnout", "hrad", "svatý", "pocit", "radost", "podlaha", "nejen", "prosit", "ztratit", "jejich", "obraz", "milovat", "jasný", "udělat", "těžko", "domácí", "láska", "podpora", "známý", "hodit", "divák", "odborník", "avšak", "vesmír", "příležitost", "rovněž", "směr", "snížit", "pozorovat", "spolu", "poměrně", "letadlo", "chlapec", "buňka", "oznámit", "nedávno", "dobře", "psát", "hlava", "život", "moře", "vyrábět", "soud", "dřevo", "výkon", "obyvatel", "jiný", "využít", "všude", "válka", "výše", "konečný", "zákazník", "nechat", "používat", "médium", "pouhý", "vláda", "během", "jakmile", "rána", "sociální", "žádat", "spát", "význam", "přinést", "docela", "látka", "máma", "popsat", "pomyslet", "opakovat", "krajina", "pivo", "nemocný", "důvod", "slovo", "ostatní", "bolest", "schod", "kamarád", "dodnes", "kapitola", "pokoj", "složka", "návrat", "vystoupit", "uvádět", "obsahovat", "častý", "společný", "výhoda", "náhle", "dnešní", "kvůli", "anebo", "poznamenat", "pozornost", "služba", "přát", "společenský", "věnovat", "stanice", "akce", "káva", "vzpomínka", "paže", "dívka", "příjemný", "orgán", "snad", "řešit", "zbytek", "obsah", "chodit", "střecha", "varianta", "posadit", "souvislost", "kluk", "zabít", "příběh", "výsledek", "dodat", "mezinárodní", "znalost", "starosta", "zatím", "rozhodnout", "výrazně", "člověk", "počátek", "kolega", "přicházet", "energie", "zmíněný", "pravděpodobně", "každý", "osoba", "místní", "současně", "ostrov", "hudba", "pustit", "sedět", "znít", "něco", "pozice", "stůl", "řízení", "krize", "stejný", "nicméně", "hlas", "opatření", "aplikace", "poté", "místo", "jeden", "končit", "prostředí", "děkovat", "krajský", "přítel", "hvězda", "nejprve", "poslední", "snadno", "zahrada", "vhodný", "loňský", "takže", "přestat", "chystat", "potvrdit", "uprostřed", "vstup", "domů", "ruský", "listopad", "květen", "protože", "rozdíl", "počasí", "barva", "předmět", "všechen", "široký", "šaty", "uvidět", "mluvčí", "připomenout", "síla", "skutečně", "projekt", "vlastně", "divadlo", "podařit", "dokonalý", "červenec", "letos", "sice", "zeptat", "vysoko", "pouze", "tušit", "černý", "výrobce", "nastat", "organizace", "pomoci", "nahoru", "nabídka", "aniž", "koleno", "situace", "letní", "maminka", "manažer", "odpovědět", "výzkum", "hudební", "reagovat", "dolů", "příští", "zjistit", "ruka", "mnohem", "sníh", "týkat", "třetí", "postupně", "pracovník", "tady", "technický", "zvuk", "zahraničí", "minulost", "přesný", "dovolit", "velikost", "vracet", "ústa", "historie", "údaj", "nalézt", "těsně", "proč", "pozemek", "většina", "zpívat", "všimnout", "proud", "starat", "zavřít", "neboť", "přesvědčit", "včetně", "vedle", "vozidlo", "politický", "dlouho", "policie", "jednat", "atmosféra", "jíst", "dokument", "potíž", "začínat", "vysoký", "zůstávat", "stav", "budoucnost", "cesta", "jinak", "třeba", "určit", "její", "odpoledne", "denně", "míra", "růst", "scéna", "název", "soutěž", "pomoc", "účel", "muzeum", "představovat", "úplně", "když", "silný", "zájem", "forma", "přístup", "zbavit", "působit", "volný", "svět", "lidský", "doba", "text", "počet", "pozdě", "správně", "zastavit", "tolik", "těžký", "zapomenout", "minuta", "objekt", "zajímavý", "skoro", "říkat", "generace", "pevný", "nemoc", "seznam", "bránit", "vysvětlovat", "potřebovat", "obecný", "dětský", "přinášet", "stejně", "příčina", "výrazný", "událost", "líbit", "nikdy", "určitě", "náklad", "karta", "čelo", "především", "poznat", "uvnitř", "onen", "vzniknout", "mluvit", "osobní", "vzít", "festival", "občas", "banka", "hodně", "vlas", "myslet", "firma", "závislý", "tradice", "elektrický", "řidič", "dokonce", "proti", "daný", "klub", "holka", "náměstí", "znát", "chlap", "závod", "verze", "chuť", "klasický", "dosud", "jedinec", "zhruba", "stávat", "vyprávět", "umožňovat", "přesně", "poprvé", "minulý", "pohyb", "dávno", "nabídnout", "problém", "nově", "dolar", "možnost", "peníze", "víno", "úvaha", "vážně", "mimo", "začít", "babička", "doplnit", "film", "užívat", "hodnota", "tradiční", "informace", "fond", "otec", "úřad", "dráha", "původní", "kariéra", "klást", "aktivní", "kolem", "pravidelně", "přežít", "ekonomický", "učitel", "duben", "sobota", "vrchol", "pozor", "nést", "uvést", "použití", "zásadní", "zavolat", "stín", "takhle", "termín", "jižní", "poskytovat", "liga", "předseda", "provoz", "trenér", "vzdálený", "datum", "jestli", "bratr", "vědomí", "teplo", "silnice", "rodinný", "nyní", "provést", "vždycky", "televize", "pražský", "moci", "okolnost", "republika", "úsměv", "internet", "normální", "vyrazit", "auto", "malý", "hezký", "rekonstrukce", "tehdy", "podnik", "reálný", "kvalita", "kilometr", "učit", "opravdu", "počkat", "poskytnout", "odborný", "přesto", "chovat", "společně", "například", "dostat", "vyjít", "chránit", "pořádek", "duch", "přijmout", "tvůj", "vztah", "odpovídat", "vrátit", "podívat", "otázka", "televizní", "poslat", "správný", "konkrétní", "vlna", "otevřený", "právní", "stačit", "chvilka", "setkání", "starý", "večer", "jistě", "vývoj", "spousta", "napětí", "vzpomínat", "jazyk", "tisíc", "hlavní", "policejní", "finanční", "výroba", "opustit", "střední", "existovat", "prohlásit", "postavit", "nový", "řídit", "žlutý", "dobrý", "leden", "soupeř", "uvedený", "připadat", "ovšem", "pomalu", "jenom", "městský", "svoboda", "deník", "pamatovat", "špatně", "noviny", "pokus", "samotný", "dosáhnout", "krok", "riziko", "projev", "literatura", "červen", "papír", "dneska", "pokud", "zítra", "těšit", "kniha", "dveře", "jaro", "vzhledem", "ředitel", "otočit", "speciální", "strana", "uživatel", "přikývnout", "fanoušek", "uvědomit", "ministerstvo", "dozvědět", "podíl", "zase", "velmi", "levý", "nějak", "považovat", "časopis", "tenhle", "ještě", "poněkud", "druhý", "blízký", "takto", "vrstva", "odjet", "zdroj", "prst", "pokoušet", "jistý", "dopis", "kdyby", "tvořit", "celý", "zatímco", "často", "bavit", "vazba", "úroveň", "požádat", "přirozený", "školní", "zažít", "majetek", "vyhrát", "navštívit", "lékař", "zařízení", "trvat", "břeh", "spokojený", "plyn", "nakonec", "miliarda", "obava", "hned", "hotový", "potkat", "herec", "základní", "součást", "vážný", "také", "test", "olej", "pohybovat", "křídlo", "přečíst", "složitý", "zemřít", "snímek", "uvědomovat", "následující", "ohled", "druh", "chování", "dost", "souhlasit", "cokoli", "hluboký", "postel", "zajímat", "chtít", "tvrdý", "vnímat", "zápas", "někde", "vstoupit", "pohled", "objevit", "skupina", "region", "tělo", "deset", "projít", "sejít", "výraz", "navíc", "bílý", "jmenovat", "smrt", "žádný", "počítač", "fotbal", "nějaký", "okolo", "zaplatit", "nemocnice", "pravidelný", "přes", "zlatý", "ležet", "vědět", "někdo", "škoda", "vůně", "ministr", "spíš", "očekávat", "překvapit", "dodávat", "zdát", "trest", "teplý", "obecně", "vydat", "přímý", "vnější", "sledovat", "mistr", "řada", "židle", "drobný", "využití", "západní", "dnes", "dějiny", "taky", "ženský", "zároveň", "stránka", "manželka", "utkání", "dorazit", "rozměr", "sklo", "charakter", "narazit", "činit", "představit", "řešení", "vědecký", "spolupráce", "milý", "evropský", "vysvětlit", "občanský", "kvalitní", "zvolit", "historický", "zůstat", "napsat", "čerstvý", "někdy", "ptát", "vyjádřit", "zrovna", "hodina", "poslouchat", "vlastnost", "armáda", "týden", "dokud", "lehký", "třída", "potřebný", "román", "čistý", "metoda", "činnost", "lidový", "konečně", "skutečný", "ukázat", "jenže", "kost", "bezpečnost", "nebe", "zbraň", "ačkoli", "země", "včera", "dotknout", "zcela", "rychlý", "bydlet", "před", "zima", "pohlédnout", "jediný", "samý", "oddělení", "nabízet", "oblast", "dřevěný", "zajistit", "napadnout", "naprosto", "zvednout", "trpět", "pokusit", "nahradit", "chápat", "získat", "patnáct", "mnohý", "vůbec", "paní", "prostor", "představa", "produkt", "pravý", "pracovní", "kámen", "budova", "dovést", "smlouva", "zahraniční", "zkušenost", "léto", "poloha", "případně", "tmavý", "večeře", "přestože", "samozřejmě", "národ", "důležitý", "policista", "schopnost", "podle", "připomínat", "padnout", "vliv", "bohatý", "nikdo", "průměr", "stěna", "uvažovat", "přijít", "pracovat", "myšlenka", "obor", "komise", "padesát", "šance", "krev", "vědec", "kousek", "díky", "záležet", "vůči", "hladina", "pole", "umět", "postup", "role", "státní", "najednou", "komunikace", "osud", "návštěva", "najít", "vidět", "délka", "měsíc", "výběr", "volba", "podmínka", "existence", "barevný", "technologie", "přijet", "rostlina", "obličej", "dopravní", "červený", "titul", "ukazovat", "veškerý", "ekonomika", "vznik", "funkce", "přírodní", "výstavba", "mnoho", "víkend", "režim", "stroj", "koupit", "dlaň", "smět", "vítězství", "svůj", "umění", "případ", "výstava", "vytvořit", "světový", "horní", "kultura", "přece", "přední", "nikoli", "naděje", "klidně", "princip", "podstata", "klient", "další", "položit", "počítat", "tábor", "nastoupit", "zákon", "světlo", "číslo", "rozhodnutí", "doufat", "pravidlo", "autor", "ozvat", "nýbrž", "požadavek", "jednání", "desítka", "mysl", "předpokládat", "zmizet", "špatný", "vycházet", "jednotlivý", "sezona", "patro", "kočka", "spatřit", "proces", "různý", "praktický", "nápad", "strom", "přidat", "celkový", "vzpomenout", "pocházet", "běžný", "procento", "předtím", "zvýšit", "dokázat", "místnost", "budoucí", "dělat", "jakýsi", "právo", "vlastní", "dařit", "věřit", "možný", "vést", "stále", "euro", "král", "krásný", "několik", "občan", "některý", "student", "park", "rodič", "areál", "stát", "obchod", "platit", "přitom", "domov", "území", "ideální", "zdraví", "práce", "rozumět", "podobně", "kuchyně", "cena", "list", "ústav", "zámek", "podporovat", "nutný", "milión", "dojít", "použít", "objem", "znovu", "technika", "model", "přístroj", "přemýšlet", "dospělý", "dispozice", "chodba", "podoba", "americký", "modrý", "ryba", "aktivita", "okamžitě", "doma", "krátce", "konstrukce", "úzký", "kolik", "životní", "rychlost", "kategorie", "pomocí", "energetický", "přičemž", "číst", "mladý", "úkol", "rameno", "nosit", "jasně", "stavební", "základ", "hlavně", "návštěvník", "církev", "okolí", "starost", "noha", "správa", "operační", "většinou", "dlouhý", "procházet", "pokračovat", "dávat", "politika", "soukromý", "vznikat", "povídat", "víra", "český", "odmítnout", "zejména", "matka", "náročný", "zabývat", "tvrdit", "oheň", "kulturní", "článek", "přímo", "přiznat", "závěr", "touha", "naučit", "dovnitř", "nástroj", "vypadat", "chyba", "nízký", "soubor", "obvyklý", "jednou", "velice", "alkohol", "povinnost", "prázdný", "vydržet", "podat", "tentýž", "teplota", "déšť", "slyšet", "agentura", "přibližně", "provádět", "tvar", "krátký", "maso", "objevovat", "partner", "nedostatek", "celkem", "hora", "odejít", "stovka", "veřejný", "ročník", "pryč", "host", "příslušný", "smích", "kůže", "jistota", "konat", "škola", "takový", "změnit", "pořád", "současný", "slabý", "potom", "šťastný", "záda", "první", "cítit", "čekat", "vždy", "veřejnost", "kancelář", "obrázek", "praxe", "trochu", "průběh", "část", "postoj", "hranice", "změna", "využívat", "prostředek", "zadní", "zvíře", "obvykle", "tedy", "dojem", "zpět", "klíčový", "nacházet", "univerzita", "dále", "rozhodně", "voda", "vítr", "péče", "podobný", "tvorba", "naopak", "obec", "umožnit", "vzdálenost", "novinka", "ráno", "jednotka", "spojení", "tiše", "předchozí", "držet", "sotva", "bota", "několikrát", "ucho", "jemný", "letošní", "mozek", "téma", "jednoduchý", "přítomnost", "hotel", "restaurace", "záležitost", "příliš", "okamžik", "připravený", "skončit", "kromě", "ulice", "brát", "daleko", "analýza", "způsobit", "docházet", "moderní", "březen", "dítě", "konec", "více", "otevřít", "ostatně", "měnit", "určitý", "centrum", "smysl", "okno", "oblíbený", "pochopit", "motor", "vyžadovat", "podzim", "prakticky", "program", "pacient", "hrozit", "vedení", "rada", "vstát", "odpověď", "málo", "kontakt", "dcera", "vesnice", "vzduch", "obrovský", "struktura", "dech", "tento", "zachránit", "fotografie", "autobus", "ztráta", "prosinec", "kapsa", "spotřeba", "volat", "duše", "vloni", "vždyť", "hledisko", "srpen", "totiž", "britský", "jaký", "strach", "jízda", "jméno", "studium", "fungovat", "významný", "úprava", "zvláštní", "čtenář", "pojem", "voják", "přejít", "hrát", "stavba", "dostávat", "útok", "kostel", "sportovní", "dívat", "proto", "aspoň", "výška", "metr", "chvíle", "zvládnout", "způsob", "deska", "zástupce", "vytvářet", "prodej", "dopadnout", "národní", "značný", "pěkný", "zpráva", "příjem", "potřeba", "nijak", "doprava", "kolo", "rámec", "manžel", "povrch", "fáze", "německý", "postava", "materiál", "stupeň", "francouzský", "vejít", "polovina", "hledat", "milimetr", "venku", "telefon", "snažit", "založit", "osobnost", "pravda", "bezpečný", "kraj", "sloužit", "možná", "neděle", "říci", "společnost", "důsledek", "bývalý", "rozpočet", "prodat", "znamenat", "člen", "hřiště", "ochrana", "bývat", "severní", "tentokrát", "branka", "rodina", "cizí", "sestra", "bojovat", "připravovat", "kontrola", "mezi", "fakt", "zbývat", "koncert", "plný", "chybět", "schopný", "umělecký", "koruna", "usmát", "spojený", "bohužel", "stopa", "dotace", "brána", "léčba", "systém", "slavný", "zpátky", "prostřednictvím", "obrátit", "jakýkoli", "návrh", "slunce", "zaměstnanec", "běžet", "styl", "obchodní", "jídlo", "muset", "fotbalový", "teprve", "dílo", "snadný", "zřejmě", "období", "připravit", "smát", "názor", "prezident", "velký", "žena", "příklad", "zdravotní", "prostě", "vadit", "neustále", "téměř", "paměť", "hráč", "alespoň", "jezdit", "majitel", "brzy", "doktor", "tvář", "rozhovor", "uzavřít", "město", "vybrat", "studie", ]
top = []
today = None
secret = None
startdate = datetime.date(2022, 5, 23)

def init():
    global today
    global secret
    with initlock:
        day = datetime.datetime.utcnow().date()
        del top[:]
        secret = None
        if today!=day:
            today=day
        else:
            return
        idx = (day-startdate).days
        try:
            secret = secrets[idx]
        except IndexError:
            print("index error, konec")
            secret = "konec"
        lst = kv.similar_by_word(secret, topn=3000)
        cnt = 0
        top.append(secret)
        for w, sim in lst:
            if cnt == 999:
                break
            if w.islower():
                top.append(w)
                cnt+=1


def check_day():
    if not today or today != datetime.datetime.utcnow().date():
        init()
    
def similarity(w1, w2):
    try:
        return float(kv.similarity(w1, w2))
    except KeyError:
        return None

def position(word):
    try:
        return top.index(word)
    except ValueError:
        return -1

def hint(best):
    try:
        i = top.index(best)
    except ValueError:
        return top[-1], len(top)-1
    if i>1:
        j = i//2
        return top[j], j
    else:
        return best, i

def giveup(best):
    try:
        i = top.index(best)
    except ValueError:
        return "chybný požadavek", -1
    if i==1:
        return top[0], 0
    else:
        return "chybný požadavek", -1


class MainHandler(tornado.web.RequestHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

    def get(self):
        check_day()
        arg = self.get_argument("type")
        attempt = self.get_argument("attempt", -1)
        remote_ip = self.request.headers.get("X-Real-IP") or \
            self.request.headers.get("X-Forwarded-For") or \
            self.request.remote_ip
        if arg == "guess":
            w = self.get_argument("word")
            sim = similarity(w, secret)
            pos = position(w)
            res = {
                "word": w,
                "sim": sim,
                "pos": pos
            }
            print(f"{remote_ip} guess {w}")
            self.write(json.dumps(res))
        elif arg == "hint":
            w = self.get_argument("best")
            h,pos = hint(w)
            print(f"{remote_ip} req {w} hint {h}")
            sim = similarity(h, secret)
            res = {
                "word": h,
                "sim": sim,
                "pos": pos,
                "hinted": True
            }
            self.write(json.dumps(res))
        elif arg == "giveup":
            w = self.get_argument("best")
            h,pos = giveup(w)
            print(f"{remote_ip} req {w} giveup {h}")
            sim = similarity(h, secret)
            res = {
                "word": h,
                "sim": sim,
                "pos": pos,
                "gave_up": True
            }
            self.write(json.dumps(res))
        else:
            self.write("K vytvoření modelu byla použita data SYN v9 a srovnávací seznamy SYN2015 z korpus.cz pod licencí CC BY 4.0.")

class MyStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

def make_app():
    return tornado.web.Application([
        (r"/api", MainHandler),
        (r'/(.*)', MyStaticFileHandler, {'path': "static", "default_filename": "index.html"}),
    ])

if __name__ == "__main__":
    print("init running")
    init()
    print("init done")
    app = make_app()
    app.listen(8888)
    print("listening")
    tornado.ioloop.IOLoop.current().start()
