# @Author : 周健
import bibtexparser
import time
import re
from tkinter import messagebox


#正则表达式：用于将latex上下标转为html上下标
pattern1=re.compile(r'\$_{(.+?)}\$')              #下标格式1
pattern2=re.compile(r'\$\^{(.+?)}\$')             #上标格式1
pattern3=re.compile(r'\\textsubscript{(.+?)}')    #下标格式2
pattern4=re.compile(r'\\textsuperscript{(.+?)}')  #上标格式2

html_escape_table = {
    '&': '&amp;',
    '--':'–',
    '"': '&quot;',
    "'": '&apos;',
    '\\alpha':'α','\\beta':'β','\\gamma':'γ','\\delta':'δ','\\epsilon':'ϵ','\\varepsilon':'ε',
    '\\zeta':'ζ','\\eta':'η','\\theta':'θ','\\iota':'ι','\\kappa':'κ','\\lambda':'λ','\\mu':'μ',
    '\\nu':'ν','\\xi':'ξ','\\omicron':'ο','\\pi':'π','\\rho':'ρ','\\sigma':'σ','\\tau':'τ',
    '\\upsilon':'υ','\\phi':'ϕ','\\varphi':'φ','\\chi':'χ','\\psi':'ψ',
    '{':'','}':'',
    }#用于将符号改为html符号，包括希腊字母

paper='<tr><td class="paperlist">order. <a href="doiurl" target="_blank">papertitle</a><br/>paperauthor<br/>source</b><button data-toggle="collapse" data-target="#bibkey" type="button" class="mybtn btn-link">bib</button><div id="bibkey" class="collapse bibtex">bibinfo</div>  </td></tr>'
#基本模板


start=time.localtime().tm_year   #获取当前时间
end=2016      #设置不再单独列出的时间终点

def readbib(bibpath):
    '''读取bib文件，并将month格式化'''
    #读取文件
    with open(bibpath,'r+',encoding='utf8') as f:
        tmp=f.read()
    #bibtex文件的month格式不加{}，导致报错
    #month    = may,变为month    = {may},
    patt_month=r'month(\s*?)=(\s*?)([a-z]{3})'
    tmp=re.sub(patt_month,lambda m:'month'+m.group(1)+'='+m.group(2)+'{'+m.group(3)+'}',tmp)
    biball=bibtexparser.loads(tmp)
    return biball

def dictbib(biball):
    '''将bib的所有条目变为时间戳对应的字典'''
    entry_dict={}
    timestamp=[]
    for item in biball.entries:
        _tmp=int(item['note'])
        timestamp.append(_tmp)
        entry_dict.update({_tmp:item})
    set_time=set(timestamp)
    if len(set_time)==len(timestamp):
        timestamp.sort(reverse=True)
        return timestamp,entry_dict
    else:
        return None,None


def change(text):
    '''替换上下标'''
    tmp=re.sub(pattern1,lambda m:'<sub>'+m.group(1)+'</sub>',text)
    tmp=re.sub(pattern3,lambda m:'<sub>'+m.group(1)+'</sub>',text)
    tmp=re.sub(pattern2,lambda m:'<sup>'+m.group(1)+'</sup>',tmp)
    tmp=re.sub(pattern4,lambda m:'<sup>'+m.group(1)+'</sup>',tmp)

    for item in html_escape_table:
        tmp=tmp.replace(item,html_escape_table[item])
    return tmp

def gettitle(bib):
    '''获取标题'''
    title=change(bib['title'])
    #title=[html_escape_table.get(c,c) for c in title]
    title=''.join(title)
    return title

def getauthor(bib):
    '''获取作者'''
    author=bib['author'].split(' and ')
    for i in range(len(author)):
        tmp=author[i]
        tmp=tmp.split(', ')
        author[i]=tmp[1]+' '+tmp[0]
    author='Author(s): '+', '.join(author)
    return author

def getsource(bib):
    '''获取出版信息'''
    if bib['ENTRYTYPE'].lower()=='article':
        #文献类型为article时
        pages=bib['pages'].replace('--','–')
        try:
            number=' ('+bib['number']+')'
        except:
            number=''
        source='Source: <b><i>'+bib['journal']+'</i>, '+bib['volume']+number+', '+pages+', '+bib['year']+'.</b>'
    elif bib['ENTRYTYPE'].lower()=='inproceedings':
        #文献类型为inproceedings时
        source='Source: <b><i>'+bib['booktitle']+'</i>, '+bib['year']+'.</b>'
    elif bib['ENTRYTYPE'].lower()=='misc':
        #文献类型为misc时，这里用misc指代已接收无DOI文章
        source='Source: <b><i>'+bib['howpublished']+'</i>, '+bib['year']+', accepted.</b>'
    return source+'&nbsp;'

def getbibinfo(bib):
    '''去除misc的输出'''
    exclued_field=['groups','ENTRYTYPE','ID','note','category','file','abstract']
    if bib['ENTRYTYPE'].lower()=='misc':
        return "暂无bib"
    else:
        bibinfo='@'+bib['ENTRYTYPE']+'{'+bib['ID']+',</br>\n'
        for item in bib:
            if item not in exclued_field:
                bibinfo=bibinfo+item+'={'+bib[item]+'},</br>\n'
        return bibinfo+'}'

def getdoiurl(bib):
    if bib['ENTRYTYPE'].lower()=='misc':
        #文献类型为misc时，这里用misc指代已接收无DOI文章
        return '#'
    else:
        return 'https://doi.org/'+bib['doi']
    
#paper='<tr><td class="paperlist">order. <a href="doiurl" target="_blank">papertitle</a><br/>paperauthor<br/>source</b><button data-toggle="collapse" data-target="#bibkey" type="button" class="mybtn btn-link">bib</button><div id="bibkey" class="collapse bibtex">bibinfo</div>  </td></tr>'
def formatitem(bib,order):
    '''获取格式化输出'''
    print('正在处理第%d个文献'%order)
    bibkey=bib['ID']
    tmp=paper.replace('order',str(order))
    tmp=tmp.replace('doiurl',getdoiurl(bib))
    tmp=tmp.replace('papertitle',gettitle(bib))
    tmp=tmp.replace('paperauthor',getauthor(bib))
    tmp=tmp.replace('source',getsource(bib))
    tmp=tmp.replace('bibkey',bibkey)
    tmp=tmp.replace('bibinfo',getbibinfo(bib))
    return tmp

def main(origin,des):
    '''主函数，生成HTML'''
    category='<tr><th class="pubyear">yearcategory</th></tr>'
    html='<table class="table">\n'
    htmlyear=0
    stop=False
    biball=readbib(bibpath=origin)
    timestamp,entry_dict=dictbib(biball)
    if timestamp==None:
        messagebox.showerror('note域重复，请检查')
    else:
        order=len(timestamp)  #加入排序
        for item in timestamp:
            bib=entry_dict[item]
            year=int(bib['year'])
            if year>end-1 and year!=htmlyear:
                newcategory=category.replace('yearcategory',bib['year'])+'\n\n'
                html=html+newcategory
                htmlyear=year
            elif not stop and year<=end-1:
                tmp=str(end)+'年之前'
                newcategory=category.replace('yearcategory',tmp)+'\n\n'
                html=html+newcategory
                stop=True
            else:
                pass
            newitem=formatitem(bib,order)
            html=html+newitem+'\n\n'
            order=order-1
        html=html+'</table>'
        with open(des,'w+',encoding='utf8') as f:
            f.write(html)

if __name__=='__main__':
    origin='./lilab.bib'
    des='./publist.html'
    main(origin,des)