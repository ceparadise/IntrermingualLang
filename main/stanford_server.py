from subprocess import Popen, PIPE

# Run this script to start StanfordNLP server

stanforNLP_server_cmd = " java -mx4g -cp * edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload tokenize,ssplit,pos,lemma,parse,depparse  -status_port 9000 -port 9000 -timeout 15000 -serverProperties StanfordCoreNLP-chinese.properties"
start_server = Popen(stanforNLP_server_cmd.split(), cwd="G:\lib\stanford-corenlp-full-2016-10-31",
                     stderr=PIPE, stdout=PIPE, shell=True)

while (True):
    line = str(start_server.stderr.readline())
    print(line)
    success_mark = 'StanfordCoreNLPServer listening at'
    except_mark = 'Address already in use'
    if success_mark in line:
        print("server started...")
        break
    elif except_mark in line:
        print("server already started or port occupied...")
        break
start_server.stderr.close()
start_server.stdout.close()
