import tkinter as tk
import socket
import json
from nltk.stem import WordNetLemmatizer
import struct

#对输入单词进行词形标准化
def lemmatize(w):
    wordnet_lemmatizer = WordNetLemmatizer()
    word1 = wordnet_lemmatizer.lemmatize(w, pos = "n") 
    word2 = wordnet_lemmatizer.lemmatize(word1, pos = "v") 
    word3 = wordnet_lemmatizer.lemmatize(word2, pos = ("a")) 
    return word3

class MainPanel:
    def __init__(self, host, port):
        # 用于连接服务器
        self.addr = (host, port)
    
    def start(self):
        """
        显示文本检索主界面
        """
        self.root = tk.Tk()
        self.root.geometry('400x400')
        self.root.title("文本检索")
        self.label = tk.Label(self.root, text="请输入检索词，用空格分隔:", font=(None, 12)).pack(pady=20)
        
        self.new_searchterm_entry = tk.Entry(self.root, font=(None, 12))
        self.new_searchterm_entry.pack()
        #精确匹配或模糊匹配两个按钮
        self.confirm_button = tk.Button(self.root, text="精确检索", font=(None,12), command=lambda:self.check_new_searchterm(0)).pack(pady=40)
        self.confirm_button_fuzzy = tk.Button(self.root, text="模糊检索", font=(None,12), command=lambda:self.check_new_searchterm(1)).pack(pady=50)
        
        self.hint_label = tk.Label(self.root, text="", font=(None, 12))
        self.hint_label.pack()
        
        self.root.mainloop()
        
    
    def check_new_searchterm(self,fuzzy):
        """
        用户点击"确认"按钮后，检查输入是否合法
        """
        searchterm = self.new_searchterm_entry.get()
        terms = searchterm.split(' ')
        terms = [lemmatize(i) for i in terms if i != '']
        if len(terms) == 0 or len(terms) > 3:
            self.hint_label.config(text=f"请输入1-3个检索词")
        else:
            print(terms)
            self.search_request(terms,fuzzy)
    
    def search_request(self, terms, fuzzy=0):
        """
        TODO: 请补充实现客户端与服务器端的通信
        
        1. 向服务器发送检索词
        2. 接受服务器返回的检索结果
        
        """
        client=socket.socket()
        client.connect((self.addr[0],self.addr[1]))
        #发送精确匹配（0）或模糊匹配（1）的信息
        bs=[False,True]
        sendbool=struct.pack('?',bs[fuzzy])
        client.send(sendbool)
        #以列表形式发送关键词
        #首先发送长度，告诉服务器接收多长的信息
        bterms=str(terms).encode('utf-8')
        sendl=struct.pack('i',len(bterms))
        client.send(sendl)
        #然后发送信息本身
        client.send(bterms)
        print('sending',str(terms),"...")
        #从服务器接收数字，知道有多少篇文章
        numofparts=eval(client.recv(0x5fffffff).decode('utf-8'))
        gettuples=[]
        print('-----------------I am informed that there are',numofparts,'to receive.---------------')
        for i in range(numofparts):
            try:
                print('--------------------现在接收第',i+1,'----------------------------------------------',end='')
                #接收并解包标题长度
                getlentitle = client.recv(4)
                gettitlesize = struct.unpack('i', getlentitle)[0]
                print('收到标题大小',end=' ')
                #接收标题
                gettitle=client.recv(gettitlesize).decode('utf-8')
                print('收到标题',end=' ')
                #接收并解包内容长度
                getconttitle = client.recv(4)
                getcontentsize = struct.unpack('i', getconttitle)[0]
                print('收到cont大小',end=' ')
                #接收内容
                getcontent=client.recv(getcontentsize).decode('utf-8')
                print('收到cont',end=' ')
                #加入答案列表中
                gettuples.append((gettitle,getcontent))
            except NameError as e:
                print('发生错误的文件：', e.__traceback__.tb_frame.f_globals['__file__'])
                print('错误所在的行号：', e.__traceback__.tb_lineno)
                print('错误信息', e)
            
        self.documents=gettuples

        client.send(''.encode('utf-8'))
        client.close()
        
        
        # 这里暂且假设获得的检索结果存储在self.documents中，并且数据格式为[(title1, doc1), (title2, doc2), ...]
        # 具体形式可以自由修改（下面几个函数中的对应内容也需要改一下）
        
        # 展示检索结果
        self.show_titles()
            
        
    def show_titles(self):
        """
        显示所有相关的文章
        
        1. 显示根据检索词搜索到的所有文章标题，使用滚动条显示（tkinter的Scrollbar控件）
        2. 点击标题，显示文章的具体内容（这里使用了 Listbox 控件的bind方法，动作为 <ListboxSelect>)
        
        """
        self.title_tk = tk.Tk()
        self.title_tk.geometry("300x300")
        self.title_tk.title("检索结果")
        self.show_listbox(self.title_tk, self.documents)
    
    def show_listbox(self, title_tk, documents):
        self.scrollbar = tk.Scrollbar(title_tk)
        self.scrollbar.pack(side='right', fill='both')
        self.listbox = tk.Listbox(title_tk, yscrollcommand=self.scrollbar.set, font=(None, 12))
        
        for doc in documents:
            self.listbox.insert("end", str(doc[0]))
        self.listbox.bind('<<ListboxSelect>>', self.show_content(documents))
        self.listbox.pack(side='left', fill='both', expand=True)
        
        
    def show_content(self, documents):
        """
        显示文档的具体内容
        """
        def callback(event):
            idx = event.widget.curselection()[0]
            content_tk = tk.Tk()
            content_tk.geometry("300x300")
            content_tk.title("显示全文")

            text = tk.Text(content_tk, font=(None, 12))
            text.config(spacing1=10)  # 调整一下行间距
            text.config(spacing2=5)
            for item in documents[idx]:
                text.insert("end", str(item) + '\n')
            text["state"] = 'disabled'
            text.pack()
            
        return callback
    
    
if __name__ == "__main__":
    host = '127.0.0.1'
    port = 1234
    gui = MainPanel(host, port)
    gui.start()