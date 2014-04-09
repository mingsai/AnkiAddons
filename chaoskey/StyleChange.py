# -*- coding: utf-8 -*-# 我的Anki插件# 作者：混沌(youliang@chaoskey.com), http://blog.chaoskey.com# 样式切换import refrom aqt import mwfrom aqt.utils import showInfofrom aqt.qt import *from anki import hooksfrom anki.cards import Cardfrom comm import onLoad,onSwitchdef appendStyle(_web,_classname):    _web.eval(u"""        document.body.className = '#classname#';        elems = document.getElementsByName('anchor');        for (var i=0;i<elems.length;i++)         {            cn=elems[i].className;            if (cn) {                cn=cn.split(' ');                cn=cn[cn.length-1];                elems[i].className='#classname# '+cn;            }        }        """.replace("#classname#",_classname))# 样式切换（可起黑夜模式的作用）class StyleManager(object):    def __init__(self):        self.midLast=None        self.classNames=None        self.classNameIndex=0        self.oldCardCss = Card.css        self.styleShortcut=QShortcut(QKeySequence("F10"), mw)        self.globalStyleShortcut=QShortcut(QKeySequence("Ctrl+F10"), mw)        self.infoShortcut=QShortcut(QKeySequence("Shift+F10"), mw)    def loadCurStyle(self):        # 优先使用全局样式，如果没有全局样式，则使用当前model的默认样式。        className=mw.col.conf.get('globalClass')        self.classNames=mw.col.conf.get('globalStyle')        if className and self.classNames:            self.midLast=0        else:            model=mw.reviewer.card.model()            self.midLast=model['id']            self.classNames=model['css']            className=model.get('defaultClassName')        self.classNames=re.findall("((\.[\w^\.]+)*\.card)(\.[\w^\.]+)* *{[^{}]+}",self.classNames)        tmp=[]        for k,_,_ in self.classNames:            if k not in tmp:                tmp.append(k)        self.classNames=[k.replace("."," ").strip() for k in tmp]        self.classNameIndex=self.classNames.index(className) if (className and className in self.classNames) else 0     def setBodyClass(self):        if mw.state != "review" and not (hasattr(mw.reviewer,"card") and mw.reviewer.card):            return        globalClass=mw.col.conf.get('globalClass')        globalStyle=mw.col.conf.get('globalStyle')        model=mw.reviewer.card.model()        if not (globalClass and globalStyle and self.midLast==0) and  self.midLast!=model['id']:            self.loadCurStyle()        if self.midLast==0:            Card.css=lambda self:"<style>%s</style>" % globalStyle        appendStyle(mw.web,self.classNames[self.classNameIndex])    def onStyleChange(self):        if mw.state != "review" and not (hasattr(mw,"reviewer") and mw.reviewer and hasattr(mw.reviewer,"card") and mw.reviewer.card):            return        globalClass=mw.col.conf.get('globalClass')        globalStyle=mw.col.conf.get('globalStyle')        model=mw.reviewer.card.model()        if not (globalClass and globalStyle and self.midLast==0) and  self.midLast!=model['id']:            self.loadCurStyle()        if len(self.classNames)<2:            if self.midLast==0:                showInfo(u"""                    无法进行样式切换，当前采用的是全局样式，并且是没有可切换项的样式。<br />                    要实现你的意图，推荐步骤：<br />                    1）你可以打开当前卡牌模板;<br />                    2）在样式栏中，增加新卡牌样式（默认样式类名是.card,新增的可选样式类名形如.yourname.card）,<br />                      你可以从<a href="http://blog.chaoskey.com/2013/07/06/201307071142">http://blog.chaoskey.com/2013/07/06/201307071142</a>找到一些范例样式；<br />                    3) Alt+F10删除全局样式，采用当前卡牌修改后的样式;<br />                    4）必要的话，你可以再次Alt+F10将当前样式应用到全局。<br />                    现在你再次按F10就可以看到样式切换效果。                    """)            else:                showInfo(u"""                    无法进行样式切换，当前采用的是当前局部样式，并且是没有可切换项的样式。<br />                    要实现你的意图，推荐步骤：<br />                    1）你可以打开当前卡牌模板;<br />                    2）在样式栏中，增加新卡牌样式（默认样式类名是.card,新增的可选样式类名形如.yourname.card）,<br />                      你可以从<a href="http://blog.chaoskey.com/2013/07/06/201307071142">http://blog.chaoskey.com/2013/07/06/201307071142</a>找到一些范例样式；<br />                    3）必要的话，你可以Alt+F10将当前样式应用到全局。<br />                    现在你再次按F10就可以看到样式切换效果。                    """)            return        self.classNameIndex+=1        if self.classNameIndex>=len(self.classNames):            self.classNameIndex=0        className=self.classNames[self.classNameIndex]        if self.midLast==0:            mw.col.conf['globalClass']=className        else:            model['defaultClassName']=className            mw.col.models.save(model)        appendStyle(mw.web,className)    def setGlobalStyle(self):        if mw.state != "review" and not (hasattr(mw,"conf") and mw.conf and hasattr(mw.reviewer,"card") and mw.reviewer.card) :            return        globalClass=mw.col.conf.get('globalClass')        globalStyle=mw.col.conf.get('globalStyle')        if globalClass and globalStyle:            showInfo(u"回到当前局部样式（再次Ctrl+F10，可将当前样式再次应用到全局）")            mw.col.conf.pop('globalClass')            mw.col.conf.pop('globalStyle')            Card.css=self.oldCardCss            self.loadCurStyle()            appendStyle(mw.web,self.classNames[self.classNameIndex])        else:            showInfo(u"将当前样式应用到全局（再次Ctrl+F10，可再次回到当前局部样式）")            model=mw.reviewer.card.model()            mw.col.conf['globalClass']=self.classNames[self.classNameIndex]            mw.col.conf['globalStyle']=globalStyle=model['css']            Card.css=lambda self:"<style>%s</style>" % globalStyle            self.midLast=0    def onInfoStyle(self):        if mw.state != "review" and not (hasattr(mw,"conf") and mw.conf and hasattr(mw.reviewer,"card") and mw.reviewer.card) :            return        showInfo(u"""            <b><font color=red >当前采用的是%s；当前样式类名%s</font></b><br />            1）F10 在当前样式(全局/局部)中，进行样式循环切换<br />            2）Ctrl+F10 将当前样式应用到全局/回到当前局部样式;<br />            3）Shift+F10 可查看当前样式状态。<br />            """%(u"全局样式" if self.midLast==0 else u"局部样式" ,self.classNames[self.classNameIndex]))    def load(self):        hooks.addHook("showQuestion", self.setBodyClass)        hooks.addHook("showAnswer", self.setBodyClass)        hooks.addHook("showReader", self.setBodyClass)        self.setBodyClass()        self.styleShortcut.connect(self.styleShortcut, SIGNAL("activated()"), self.onStyleChange)        self.globalStyleShortcut.connect(self.globalStyleShortcut, SIGNAL("activated()"), self.setGlobalStyle)        self.infoShortcut.connect(self.infoShortcut, SIGNAL("activated()"), self.onInfoStyle)    def unload(self):        hooks.remHook("showQuestion", self.setBodyClass)        hooks.remHook("showAnswer", self.setBodyClass)        hooks.remHook("showReader", self.setBodyClass)        self.styleShortcut.disconnect(self.styleShortcut, SIGNAL("activated()"), self.onStyleChange)        self.globalStyleShortcut.disconnect(self.globalStyleShortcut, SIGNAL("activated()"), self.setGlobalStyle)        self.infoShortcut.disconnect(self.infoShortcut, SIGNAL("activated()"), self.onInfoStyle)        Card.css=self.oldCardCss        if mw.state == "review" and hasattr(mw.reviewer,"card") and mw.reviewer.card:            mw.web.eval(u"document.body.className = 'card card%d';"%mw.reviewer.card.ord)styleManager=StyleManager()def load():    styleManager.load()def unload():    styleManager.unload()# 本模块的信息ModuleInfo = {'name': u'样式切换\tF10'}plugName=os.path.basename(__file__).replace(".py", "")# 添加功能开关action=QAction(ModuleInfo["name"], mw)action.setCheckable(True)action.connect(action, SIGNAL("triggered()"),lambda:onSwitch(load,unload,action,plugName))ModuleInfo.update({"action":action})# 功能加载onLoad(load,action,plugName)