import sys,os  
  
def afileline(f_path):  
    res=0  
    print f_path
    f=open(f_path,"r")  
    for lines in f:  
        if(lines.split()):  
            res+=1  
    return res  
  
if(__name__=='__main__'):  
    host='.'  
    allline=0  
    allfiles=0  
    for root,dirs,files in os.walk(host):  
        if(root.startswith(host+os.sep+'app/static')):  
            continue  
        if(root.startswith(host+os.sep+'.git')):  
            continue  
        if(root.startswith(host+os.sep+'.idea')):  
            continue  
        if(root.startswith(host+os.sep+'migrations')):  
            continue  
        for afile in files:  
            ext=afile.split('.')  
            ext=ext[-1]  
            if(ext in ['py','html','txt', 'js', 'css']):  
                itpath=root+os.sep+afile  
                allfiles+=1  
                allline+=afileline(itpath)  
    print ('Total lines:',allline)  
    print ('Total: ',allfiles) 