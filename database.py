from py2neo import Graph,Node
from sklearn.feature_extraction.text import CountVectorizer
import joblib


graph = Graph("bolt://localhost:7687", auth=("neo4j", "Mm03007493358"))
def Create_user(uname,uemail,upass,ip_add):
    node1 = Node("Person", name=uname, email = uemail,password = upass,ip=ip_add)
    graph.create(node1)
#ret = graph.run("""MATCH(n:Person) where n.email  ="minhalawais@gmail.com" with COUNT(n)>0 as user_exists Return user_exists""").__str__()
def predict_gender(name):
    model = joblib.load("gender_detect.pkl")
    vectorizer = CountVectorizer()
    vocabulary = joblib.load("vocabulary.pkl")
    vectorizer.vocabulary_ = vocabulary
    name_vectorized = vectorizer.transform([name])
    predicted_gender = model.predict(name_vectorized)[0]
    return predicted_gender
def get_name(email):
    user = graph.run("""MATCH(n:Person) where n.email  = $email return n.name""",email=email).data()
    if user:
        return user[0]["n.name"]
    return False
def check_email(uemail):
    user = graph.run("""MATCH(n:Person) where n.email  = $uemail with COUNT(n)>0 as user_exists Return user_exists""",uemail=uemail).data()
    if user[0]["user_exists"]:
        return True
    else:
        return False
def get_pass(email):
    pass1 = graph.run("""MATCH(n:Person) where n.email  = $email Return n.password""", email=email).data()
    return pass1[0]["n.password"]

def get_ip(email):
    ip = graph.run("""MATCH(n:Person) where n.email  = $email Return n.ip""", email=email).data()
    return ip[0]["n.ip"]
def update_ip(email,ip):
    ip = graph.run("""Match(n:Person{email:$email})set n.ip = $ip return n.ip""",email=email,ip=ip).data()
    return ip[0]["n.ip"]
def update_password(email,new_pass):
    graph.run("""Match(n:Person{email:$email})set n.password = $new_pass""", email=email, new_pass=new_pass).data()
def get_edpisode_date(email,episode):
    date = graph.run("""match(p:Person{email:$email})-[:has]->(e:episode{name:$name}) return e.date """,email=email,name=episode).data()
    return date[0]["e.date"]
def findRelation(email):
    ip = get_ip(email)
    name_list = graph.run("""Match(n:Person) where n.ip=$ip and not(n.email = $email) return n.name""",ip=ip,email = email).data()
    for names in name_list:
        temp = graph.run("""MATCH (a:Person),(b:Person) WHERE NOT EXISTS {(a)-[*]->(b)} and a.email = $email and b.name = $names["n.name"] RETURN b.name""",email=email,names=names).data()
        if temp:
            return temp[0]["b.name"]
def create_relation(name1,email):
    graph.run("""MATCH (p1:Person {email: $email}), (p2:Person {name: $name1}) CREATE (p1)-[:KNOWS]->(p2)""",name1=name1,email=email)

def set_gender(email,gender):
    graph.run("""match(p:Person {email:$email}) set p.gender = $gender""",email=email,gender=gender)

def get_gender(email):
    gender = graph.run("""match(p:Person {email:$email}) return p.gender""",email=email).data()
    if gender:
        return gender[0]["p.gender"]
    return False
def create_episode(email,name,date,chat):
    graph.run("""match (p:Person{email:$email}) create(p)-[:has]->(e:episode{name:$name,date:$date,chat:$chat})""",email=email,chat=chat,name = name,date = date)
def update_episode(email,date,chat):
    check = graph.run("""match(p:Person{email:$email})-[:has]->(e:episode) return e.name""",email=email).data()
    date = str(date)
    chat = "\n"+chat
    string = ""
    if check:
        for episode in check:
            string = string +episode["e.name"]
        if "episode1" in string:
            if "episode2" in string:
                if date == get_edpisode_date(email,"episode2"):
                    old_chat = graph.run("""match(p:Person{email:$email})-[:has]->(e:episode{name:$name}) return e.chat """,email=email,name="episode2").data()
                    chat = old_chat[0]["e.chat"] + chat
                    graph.run("""match(p:Person{email:$email})-[:has]->(e:episode{name:$name}) set e.chat = $chat""",email=email,chat=chat,name="episode2")
                else:
                    graph.run("""match(p:Person{email:$email})-[:has]->(e:episode{name:$name}) set e.chat = $chat""",
                              email=email, chat=chat, name="episode2")
            elif date == get_edpisode_date(email,"episode1"):
                old_chat = graph.run("""match(p:Person{email:$email})-[:has]->(e:episode{name:$name}) return e.chat """,
                                     email=email, name="episode1").data()
                chat = old_chat[0]["e.chat"] + chat
                graph.run("""match(p:Person{email:$email})-[:has]->(e:episode{name:$name}) set e.chat = $chat""",
                          email=email, chat=chat, name="episode1")
            else:
                create_episode(email,"episode2",date,chat)
    else:
        create_episode(email,"episode1",date,chat)

def get_episode_chat(email):
    check = graph.run("""match(p:Person{email:$email})-[:has]->(e:episode) return e.name""", email=email).data()
    string = ""
    if check:
        for episode in check:
            string = string +episode["e.name"]
            if "episode2" in string:
                chat = graph.run("""match(p:Person{email:$email})-[:has]->(e:episode{name:"episode2"}) return e.chat""",email=email).data()
                return chat[0]["e.chat"]
            else:
                    chat = graph.run("""match(p:Person{email:$email})-[:has]->(e:episode{name:"episode1"}) return e.chat""",email=email).data()
                    return chat[0]["e.chat"]
    return False
def update_norelation(email,name):
    old_rel = graph.run("""match(p:Person{email:$email}) return p.norelation""",email=email).data()
    if old_rel[0]["p.norelation"]:
        old_rel[0]["p.norelation"] =  old_rel[0]["p.norelation"] + " , " + name
        name = old_rel[0]["p.norelation"]
    graph.run("""match(p:Person{email:$email}) set p.norelation = $name return p""",email=email,name=name)
def get_norelation(email):
    old_rel = graph.run("""match(p:Person{email:$email}) return p.norelation""", email=email).data()
    old_rel = old_rel[0]["p.norelation"]
    return old_rel

def create_social_network(name1,name2,relation):
    b = Node("Person",name=name2)
    graph.run(f"MATCH (a:Person) Where a.name=$name1 Create (a)-[:{relation}]->($b)",name1=name1,b=b)
