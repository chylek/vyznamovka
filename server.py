import gensim
from pytz import UTC
import tornado.ioloop
import tornado.web
import datetime
import json

w2v_path = "cs_syn_vectors.bin"
kv = gensim.models.KeyedVectors.load_word2vec_format(w2v_path, binary=True)
secrets = ["knihovna", "noční", "patřit", "množství", "operace", "blízko", "právě", "píseň", "investice", "následovat", "hovořit", "skutečnost", "vnitřní", "rychle", "jestliže", "opět", "promluvit", "politik", "teorie", "spojit", "skvělý", "táta", "drahý", "navrhnout", "hrad", "svatý", "pocit", "radost", "podlaha", "nejen", "prosit", "ztratit", "jejich", "obraz", "milovat", "jasný", "udělat", "těžko", "domácí", "láska", "podpora", "známý", "hodit", "divák", "odborník", "avšak", "vesmír", "příležitost", "rovněž", "směr", "snížit", "pozorovat", "spolu", "poměrně", "obsahovat", "ústa", "místo", "bolest", "vysoko", "schod", "uprostřed", "účel", "energie", "vstup", "pozornost", "starat", "zastavit", "život", "míra", "sedět", "postupně", "rána", "velikost", "mezinárodní", "dnešní", "hlava", "událost", "divadlo", "zeptat", "příčina", "vzpomínka", "loňský", "příběh", "mluvit", "pokoj", "konečný", "proud", "buňka", "chystat", "líbit", "náhle", "vracet", "potřebovat", "dobře", "představovat", "text", "muzeum", "pozemek", "přicházet", "příjemný", "dívka", "pravděpodobně", "přítel", "letos", "historie", "souvislost", "zjistit", "nemocný", "orgán", "sníh", "válka", "soutěž", "dokonalý", "scéna", "krajský", "zapomenout", "šaty", "zajímavý", "akce", "máma", "koleno", "potíž", "firma", "návrat", "zahraničí", "dokument", "pomoci", "střecha", "přesný", "objekt", "většina", "pracovník", "počátek", "říkat", "znít", "dolů", "denně", "začínat", "stejný", "údaj", "kamarád", "technický", "všimnout", "popsat", "řešit", "obsah", "pomoc", "snadno", "atmosféra", "stanice", "projekt", "vláda", "kapitola", "krize", "růst", "pivo", "manažer", "určit", "tušit", "společný", "končit", "zmíněný", "výrazný", "závislý", "reagovat", "festival", "poznat", "náklad", "zbytek", "častý", "bránit", "doba", "vhodný", "potvrdit", "zavřít", "káva", "odpovědět", "minulost", "lidský", "připomenout", "slovo", "nemoc", "občas", "rozhodnout", "vlas", "policie", "posadit", "chlapec", "síla", "podařit", "politický", "letní", "zbavit", "přát", "vysvětlovat", "uvádět", "široký", "dřevo", "nahoru", "barva", "zpívat", "kluk", "rozdíl", "děkovat", "dodat", "výsledek", "hvězda", "zvuk", "dětský", "jíst", "kolega", "zájem", "situace", "ruka", "stůl", "opatření", "zákazník", "název", "cesta", "maminka", "vzít", "hudba", "paže", "zahrada", "seznam", "forma", "odpoledne", "výrobce", "látka", "vozidlo", "moře", "hudební", "letadlo", "starosta", "služba", "svět", "řízení", "pozice", "výzkum", "výrazně", "pevný", "obyvatel", "krajina", "výhoda", "nalézt", "hlas", "místní", "znalost", "nabídka", "soud", "chodit", "uvidět" ]
top = []
today = None
secret = None
startdate = datetime.date(2022, 5, 23)

def init():
    global today
    global secret
    day = datetime.datetime.utcnow().date()
    if today!=day:
        today=day
    else:
        return
    del top[:]
    secret = None
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
    if i>10:
        j = i//2
        return top[j], j
    elif i>1:
        j = i-1
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
        # attempt = self.get_argument("attempt", -1)
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
            self.write("Hello world.")

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
