BUFFER=[]
def push(e): BUFFER.append(e); del BUFFER[:-500]
def recent(): return BUFFER
